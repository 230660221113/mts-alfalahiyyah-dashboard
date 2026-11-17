-- Jalankan di Supabase SQL Editor.
create table public.profiles (
  id   uuid primary key references auth.users(id) on delete cascade,
  nama text not null default '',
  role text not null default 'pimpinan' check (role in ('operator','pimpinan'))
);

create table public.siswa_rekap (
  id           bigint generated always as identity primary key,
  tahun_ajaran text not null check (tahun_ajaran ~ '^\d{4}/\d{4}$'),
  kelas        text not null check (kelas in ('VII','VIII','IX')),
  laki_laki    integer not null check (laki_laki >= 0),
  perempuan    integer not null check (perempuan >= 0),
  updated_by   uuid default auth.uid(),
  updated_at   timestamptz not null default now(),
  unique (tahun_ajaran, kelas)
);

create or replace function public.app_role() returns text
language sql stable security definer set search_path = public as
$$ select role from public.profiles where id = auth.uid() $$;

-- Profil otomatis (default: pimpinan). Naikkan ke operator secara manual.
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as
$$ begin insert into public.profiles(id) values (new.id); return new; end $$;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

alter table public.profiles    enable row level security;
alter table public.siswa_rekap enable row level security;

create policy "profil sendiri" on public.profiles
  for select to authenticated using (id = auth.uid());

create policy "semua peran membaca" on public.siswa_rekap
  for select to authenticated using (public.app_role() in ('operator','pimpinan'));
create policy "operator menambah" on public.siswa_rekap
  for insert to authenticated with check (public.app_role() = 'operator');
create policy "operator mengubah" on public.siswa_rekap
  for update to authenticated using (public.app_role() = 'operator')
  with check (public.app_role() = 'operator');
create policy "operator menghapus" on public.siswa_rekap
  for delete to authenticated using (public.app_role() = 'operator');

-- Contoh menjadikan seseorang operator:
-- update public.profiles set role='operator', nama='Nama' where id = '<uuid-user>';
