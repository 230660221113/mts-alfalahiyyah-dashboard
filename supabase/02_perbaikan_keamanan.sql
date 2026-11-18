-- ============================================================================
-- 02_perbaikan_keamanan.sql  —  MTs Al-Falahiyyah
-- Jalankan SEKALI di Supabase > SQL Editor, setelah schema.sql.
-- Dibungkus transaksi: kalau ada satu error, semua perubahan dibatalkan.
-- Memperbaiki: (1) naik pangkat lewat profiles, (2) view rekap salah untuk
-- tahun lama, (3) data identitas siswa terbuka untuk kepala sekolah.
-- ============================================================================
begin;

-- Fungsi pembantu: tambahkan search_path agar aman (security definer)
create or replace function public.is_operator()
returns boolean language sql security definer stable set search_path = public as $$
  select exists (
    select 1 from public.profiles
    where id = auth.uid() and role = 'operator' and aktif = true
  );
$$;

-- ---------------------------------------------------------------------------
-- 1. PROFILES: pengguna tidak boleh mengubah role / status aktif miliknya
-- ---------------------------------------------------------------------------
drop policy if exists "baca_semua_auth_profiles"          on public.profiles;
drop policy if exists "update_profiles_operator_or_self"  on public.profiles;
drop policy if exists "baca_profil_sendiri_atau_op"       on public.profiles;
drop policy if exists "update_profil_operator"            on public.profiles;
drop policy if exists "update_profil_sendiri"             on public.profiles;

create policy "baca_profil_sendiri_atau_op" on public.profiles
  for select to authenticated
  using (id = auth.uid() or public.is_operator());

create policy "update_profil_operator" on public.profiles
  for update to authenticated
  using (public.is_operator()) with check (public.is_operator());

-- Pengguna biasa boleh mengubah profilnya sendiri, tetapi role dan aktif harus tetap sama
create policy "update_profil_sendiri" on public.profiles
  for update to authenticated
  using (id = auth.uid())
  with check (
    id = auth.uid()
    and role  = (select p.role  from public.profiles p where p.id = auth.uid())
    and aktif = (select p.aktif from public.profiles p where p.id = auth.uid())
  );

-- Akun baru SELALU kepala_sekolah. Role dari metadata pendaftaran diabaikan,
-- supaya orang tidak bisa mendaftar sendiri sebagai operator.
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, username, nama, jabatan, role)
  values (
    new.id,
    split_part(new.email, '@', 1),
    coalesce(new.raw_user_meta_data->>'nama', split_part(new.email, '@', 1)),
    coalesce(new.raw_user_meta_data->>'jabatan', 'Kepala Sekolah'),
    'kepala_sekolah'
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

-- Pengaturan: sebelum login hanya nama madrasah dan WA operator yang terbaca
drop policy if exists "baca_pengaturan" on public.master_pengaturan;
create policy "baca_pengaturan" on public.master_pengaturan
  for select
  using (kunci in ('nama_madrasah', 'wa_operator') or auth.uid() is not null);

-- ---------------------------------------------------------------------------
-- 2. IDENTITAS SISWA: hanya operator yang boleh membaca tabel mentah
--    (kepala sekolah memakai view agregat di bawah)
-- ---------------------------------------------------------------------------
drop policy if exists "baca_siswa"          on public.master_siswa;
drop policy if exists "baca_riwayat_aktif"  on public.riwayat_siswa_aktif;
drop policy if exists "baca_riwayat_alumni" on public.riwayat_alumni;
drop policy if exists "baca_log"            on public.log_unggah_data;

create policy "baca_siswa_op"          on public.master_siswa        for select to authenticated using (public.is_operator());
create policy "baca_riwayat_aktif_op"  on public.riwayat_siswa_aktif for select to authenticated using (public.is_operator());
create policy "baca_riwayat_alumni_op" on public.riwayat_alumni      for select to authenticated using (public.is_operator());
create policy "baca_log_op"            on public.log_unggah_data     for select to authenticated using (public.is_operator());

-- ---------------------------------------------------------------------------
-- 3. VIEW AGREGAT (tanpa NIK/nama). Dijalankan dengan hak pemilik view,
--    jadi tetap bisa dibaca kepala sekolah walau tabel mentah dibatasi.
-- ---------------------------------------------------------------------------
-- Perbaikan: syarat status_terkini dihapus (membuat L+P < total di tahun lama)
-- dan tahun tanpa data aktif dibuang (agar tidak muncul sebagai angka 0 di deret waktu).
create or replace view public.v_rekap_siswa_aktif as
select
  ta.tahun_ajaran,
  ta.tahun_mulai,
  count(rsa.nik) filter (where mk.tingkat = 'VII')  as kelas_vii,
  count(rsa.nik) filter (where mk.tingkat = 'VIII') as kelas_viii,
  count(rsa.nik) filter (where mk.tingkat = 'IX')   as kelas_ix,
  count(rsa.nik)                                    as total_aktif,
  count(rsa.nik) filter (where ms.jenis_kelamin = 'L') as total_laki,
  count(rsa.nik) filter (where ms.jenis_kelamin = 'P') as total_perempuan
from public.master_tahun_ajaran ta
join public.riwayat_siswa_aktif rsa on rsa.tahun_ajaran = ta.tahun_ajaran
join public.master_kelas mk on mk.kode_kelas = rsa.kode_kelas
join public.master_siswa ms on ms.nik = rsa.nik
group by ta.tahun_ajaran, ta.tahun_mulai
order by ta.tahun_mulai asc;

create or replace view public.v_rekap_alumni as
select
  ra.tahun_ajaran_lulus as tahun_ajaran,
  count(*)                                         as total_alumni,
  count(*) filter (where ms.jenis_kelamin = 'L')   as total_laki,
  count(*) filter (where ms.jenis_kelamin = 'P')   as total_perempuan
from public.riwayat_alumni ra
join public.master_siswa ms on ms.nik = ra.nik
group by ra.tahun_ajaran_lulus
order by ra.tahun_ajaran_lulus;

-- Hanya pengguna yang sudah login yang boleh membaca view (anon ditutup)
revoke all on public.v_rekap_siswa_aktif from anon, public;
revoke all on public.v_rekap_alumni      from anon, public;
grant select on public.v_rekap_siswa_aktif to authenticated;
grant select on public.v_rekap_alumni      to authenticated;

commit;
notify pgrst, 'reload schema';

-- ============================================================================
-- PENGECEKAN (jalankan terpisah setelah selesai)
-- ============================================================================
-- a) Konsistensi: baris yang dikembalikan harus KOSONG
--    select * from public.v_rekap_siswa_aktif where total_laki + total_perempuan <> total_aktif;
-- b) Uji naik pangkat. Ganti UUID dengan id akun kepala sekolah. Harus GAGAL
--    ("violates row-level security policy"):
--    begin;
--    set local role authenticated;
--    select set_config('request.jwt.claims', '{"sub":"UUID_KEPSEK","role":"authenticated"}', true);
--    update public.profiles set role = 'operator' where id = 'UUID_KEPSEK';
--    rollback;
-- c) Kepala sekolah tidak boleh melihat identitas. Harus 0 baris:
--    begin;
--    set local role authenticated;
--    select set_config('request.jwt.claims', '{"sub":"UUID_KEPSEK","role":"authenticated"}', true);
--    select count(*) from public.master_siswa;
--    rollback;
