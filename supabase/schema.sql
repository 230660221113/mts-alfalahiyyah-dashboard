-- ============================================================================
-- SKEMA BASIS DATA TERNORMALISASI 3NF — MTs AL-FALAHIYYAH
-- Memisahkan Tabel Master (Referensi) dan Tabel Transaksi Riwayat (Aktif vs Alumni)
-- ============================================================================

-- 1. TABEL MASTER PENGGUNA & PENGATURAN SISTEM
create table if not exists public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  username    text unique,
  nama        text not null default '',
  jabatan     text not null default 'Staf Madrasah',
  no_wa       text default '',
  role        text not null default 'kepala_sekolah'
              check (role in ('operator','kepala_sekolah')),
  aktif       boolean not null default true,
  created_at  timestamptz not null default now()
);

create table if not exists public.master_pengaturan (
  kunci       text primary key,
  nilai       text not null,
  keterangan  text,
  updated_at  timestamptz not null default now()
);

insert into public.master_pengaturan (kunci, nilai, keterangan) values
  ('nama_madrasah', 'MTs Al-Falahiyyah', 'Nama resmi madrasah'),
  ('wa_operator', '6281234567890', 'Nomor WhatsApp Operator Super Admin untuk bantuan lupa kata sandi'),
  ('kapasitas_rombel', '32', 'Kapasitas maksimal siswa per rombongan belajar (Permendikbud/Kemenag)'),
  ('rasio_guru_siswa', '20', 'Rasio ideal jumlah siswa per guru mata pelajaran')
on conflict (kunci) do nothing;

-- 2. TABEL MASTER TAHUN AJARAN (3NF: Menghindari duplikasi label & urutan tahun)
create table if not exists public.master_tahun_ajaran (
  tahun_ajaran  text primary key check (tahun_ajaran ~ '^[0-9]{4}/[0-9]{4}$'),
  tahun_mulai   int not null unique,
  tahun_selesai int not null unique,
  is_aktif      boolean not null default false
);

-- 3. TABEL MASTER KELAS / ROMBEL (3NF: Tingkat & Rombel terpisah dari data siswa)
create table if not exists public.master_kelas (
  kode_kelas    text primary key,
  tingkat       text not null check (tingkat in ('VII','VIII','IX')),
  nama_rombel   text not null,
  kapasitas     int not null default 32
);

insert into public.master_kelas (kode_kelas, tingkat, nama_rombel, kapasitas) values
  ('VII-A', 'VII', 'Kelas VII-A', 32),
  ('VII-B', 'VII', 'Kelas VII-B', 32),
  ('VIII-A', 'VIII', 'Kelas VIII-A', 32),
  ('VIII-B', 'VIII', 'Kelas VIII-B', 32),
  ('IX-A', 'IX', 'Kelas IX-A', 32),
  ('IX-B', 'IX', 'Kelas IX-B', 32)
on conflict (kode_kelas) do nothing;

-- 4. TABEL MASTER SISWA (3NF: Atribut identitas melekat pada NIK 16 digit sebagai Primary Key)
create table if not exists public.master_siswa (
  nik             char(16) primary key check (nik ~ '^[0-9]{16}$'),
  nisn            char(10) unique check (nisn is null or nisn ~ '^[0-9]{10}$'),
  nama_lengkap    text not null,
  jenis_kelamin   char(1) not null check (jenis_kelamin in ('L','P')),
  tempat_lahir    text default '',
  tanggal_lahir   date,
  status_terkini  text not null default 'Aktif' check (status_terkini in ('Aktif','Alumni','Mutasi')),
  updated_at      timestamptz not null default now()
);

-- 5. TABEL TRANSAKSI: RIWAYAT SISWA AKTIF PER TAHUN AJARAN
create table if not exists public.riwayat_siswa_aktif (
  id              bigserial primary key,
  nik             char(16) not null references public.master_siswa(nik) on update cascade on delete cascade,
  tahun_ajaran    text not null references public.master_tahun_ajaran(tahun_ajaran) on update cascade,
  kode_kelas      text not null references public.master_kelas(kode_kelas) on update cascade,
  created_at      timestamptz not null default now(),
  unique (nik, tahun_ajaran)
);

-- 6. TABEL TRANSAKSI: RIWAYAT ALUMNI / LULUSAN (Terpisah dari siswa aktif)
create table if not exists public.riwayat_alumni (
  nik                 char(16) primary key references public.master_siswa(nik) on update cascade on delete cascade,
  tahun_masuk         int,
  tahun_lulus         int not null,
  tahun_ajaran_lulus  text not null references public.master_tahun_ajaran(tahun_ajaran) on update cascade,
  no_ijazah           text default '',
  melanjutkan_ke      text default '',
  created_at          timestamptz not null default now()
);

-- 7. TABEL AUDIT LOG UNGGAHAN DATA
create table if not exists public.log_unggah_data (
  id              bigserial primary key,
  jenis_unggah    text not null check (jenis_unggah in ('Siswa Aktif','Alumni')),
  nama_file       text not null,
  jumlah_baris    int not null default 0,
  diunggah_oleh   uuid references auth.users(id),
  created_at      timestamptz not null default now()
);

-- ============================================================================
-- VIEW AGREGASI UNTUK ANALITIK & PEMODELAN PREDIKSI (Hanya menghitung Siswa Aktif)
-- ============================================================================
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
left join public.riwayat_siswa_aktif rsa on rsa.tahun_ajaran = ta.tahun_ajaran
left join public.master_kelas mk on mk.kode_kelas = rsa.kode_kelas
left join public.master_siswa ms on ms.nik = rsa.nik and ms.status_terkini = 'Aktif'
group by ta.tahun_ajaran, ta.tahun_mulai
order by ta.tahun_mulai asc;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) & TRIGGER OTOMATIS PROFIL
-- ============================================================================
alter table public.profiles enable row level security;
alter table public.master_pengaturan enable row level security;
alter table public.master_tahun_ajaran enable row level security;
alter table public.master_kelas enable row level security;
alter table public.master_siswa enable row level security;
alter table public.riwayat_siswa_aktif enable row level security;
alter table public.riwayat_alumni enable row level security;
alter table public.log_unggah_data enable row level security;

-- Helper function cek operator
create or replace function public.is_operator()
returns boolean language sql security definer stable as $$
  select exists (
    select 1 from public.profiles where id = auth.uid() and role = 'operator' and aktif = true
  );
$$;

-- Policy baca untuk semua pengguna terautentikasi
create policy "baca_semua_auth_profiles" on public.profiles for select to authenticated using (true);
create policy "update_profiles_operator_or_self" on public.profiles for update to authenticated using (id = auth.uid() or public.is_operator());

create policy "baca_pengaturan" on public.master_pengaturan for select using (true);
create policy "kelola_pengaturan_op" on public.master_pengaturan for all to authenticated using (public.is_operator()) with check (public.is_operator());

create policy "baca_ta" on public.master_tahun_ajaran for select to authenticated using (true);
create policy "kelola_ta_op" on public.master_tahun_ajaran for all to authenticated using (public.is_operator()) with check (public.is_operator());

create policy "baca_kelas" on public.master_kelas for select to authenticated using (true);
create policy "kelola_kelas_op" on public.master_kelas for all to authenticated using (public.is_operator()) with check (public.is_operator());

create policy "baca_siswa" on public.master_siswa for select to authenticated using (true);
create policy "kelola_siswa_op" on public.master_siswa for all to authenticated using (public.is_operator()) with check (public.is_operator());

create policy "baca_riwayat_aktif" on public.riwayat_siswa_aktif for select to authenticated using (true);
create policy "kelola_riwayat_aktif_op" on public.riwayat_siswa_aktif for all to authenticated using (public.is_operator()) with check (public.is_operator());

create policy "baca_riwayat_alumni" on public.riwayat_alumni for select to authenticated using (true);
create policy "kelola_riwayat_alumni_op" on public.riwayat_alumni for all to authenticated using (public.is_operator()) with check (public.is_operator());

create policy "baca_log" on public.log_unggah_data for select to authenticated using (true);
create policy "tulis_log_op" on public.log_unggah_data for insert to authenticated with check (public.is_operator());

-- Trigger otomatis sinkronisasi saat user baru dibuat di Supabase Auth
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, username, nama, jabatan, role)
  values (
    new.id,
    split_part(new.email, '@', 1),
    coalesce(new.raw_user_meta_data->>'nama', split_part(new.email, '@', 1)),
    coalesce(new.raw_user_meta_data->>'jabatan', 'Kepala Sekolah'),
    coalesce(new.raw_user_meta_data->>'role', 'kepala_sekolah')
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
