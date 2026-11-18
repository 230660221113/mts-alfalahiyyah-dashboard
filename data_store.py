import os
import pandas as pd
import streamlit as st

try:
    from supabase import create_client, Client
except Exception:
    create_client = None
    Client = None


def is_supabase_configured() -> bool:
    try:
        url = st.secrets.get("SUPABASE_URL", "") or os.getenv("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "") or os.getenv("SUPABASE_KEY", "")
        return bool(url and key and "supabase.co" in url and create_client is not None)
    except Exception:
        return False


def get_supabase() -> "Client | None":
    """Satu klien PER SESI pengguna (disimpan di session_state), bukan satu klien bersama."""
    if not is_supabase_configured():
        return None
    if "_sb" not in st.session_state:
        url = st.secrets.get("SUPABASE_URL", "") or os.getenv("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "") or os.getenv("SUPABASE_KEY", "")
        st.session_state["_sb"] = create_client(url, key)
    return st.session_state["_sb"]


def init_demo_state():
    """Inisialisasi state lokal hanya jika Supabase belum terpasang."""
    if "demo_users" not in st.session_state:
        st.session_state["demo_users"] = {
            "operator@alfalahiyyah.sch.id": {
                "password": "operator123",
                "nama": "Operator MTs Al-Falahiyyah",
                "jabatan": "Operator EMIS / Super Admin",
                "role": "operator",
                "aktif": True,
            },
            "kepsek@alfalahiyyah.sch.id": {
                "password": "kepsek123",
                "nama": "Kepala MTs Al-Falahiyyah",
                "jabatan": "Kepala Madrasah",
                "role": "kepala_sekolah",
                "aktif": True,
            },
        }
    if "demo_settings" not in st.session_state:
        st.session_state["demo_settings"] = {
            "nama_madrasah": "MTs Al-Falahiyyah",
            "wa_operator": "6281234567890",
            "kapasitas_rombel": "32",
            "rasio_guru_siswa": "20",
        }
    if "demo_rekap" not in st.session_state:
        st.session_state["demo_rekap"] = pd.DataFrame([
            {"tahun_ajaran": "2020/2021", "tahun_mulai": 2020, "kelas_vii": 62, "kelas_viii": 58, "kelas_ix": 55, "total_aktif": 175, "total_laki": 89, "total_perempuan": 86},
            {"tahun_ajaran": "2021/2022", "tahun_mulai": 2021, "kelas_vii": 68, "kelas_viii": 61, "kelas_ix": 57, "total_aktif": 186, "total_laki": 95, "total_perempuan": 91},
            {"tahun_ajaran": "2022/2023", "tahun_mulai": 2022, "kelas_vii": 74, "kelas_viii": 67, "kelas_ix": 60, "total_aktif": 201, "total_laki": 103, "total_perempuan": 98},
            {"tahun_ajaran": "2023/2024", "tahun_mulai": 2023, "kelas_vii": 79, "kelas_viii": 73, "kelas_ix": 66, "total_aktif": 218, "total_laki": 111, "total_perempuan": 107},
            {"tahun_ajaran": "2024/2025", "tahun_mulai": 2024, "kelas_vii": 85, "kelas_viii": 78, "kelas_ix": 72, "total_aktif": 235, "total_laki": 118, "total_perempuan": 117},
            {"tahun_ajaran": "2025/2026", "tahun_mulai": 2025, "kelas_vii": 92, "kelas_viii": 84, "kelas_ix": 77, "total_aktif": 253, "total_laki": 127, "total_perempuan": 126},
        ])
    if "demo_alumni_count" not in st.session_state:
        st.session_state["demo_alumni_count"] = 184


def get_settings() -> dict:
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("master_pengaturan").select("kunci, nilai").execute()
            data = {r["kunci"]: r["nilai"] for r in (res.data or [])}
            if data:
                return data
        except Exception:
            pass
    init_demo_state()
    return st.session_state["demo_settings"]


def save_setting(kunci: str, nilai: str):
    sb = get_supabase()
    if sb:
        sb.table("master_pengaturan").upsert({"kunci": kunci, "nilai": str(nilai)}).execute()
    else:
        init_demo_state()
        st.session_state["demo_settings"][kunci] = str(nilai)


def get_rekap_siswa_aktif() -> pd.DataFrame:
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("v_rekap_siswa_aktif").select("*").order("tahun_mulai").execute()
            return pd.DataFrame(res.data or [])
        except Exception:
            return pd.DataFrame()
    init_demo_state()
    return st.session_state["demo_rekap"].copy()


def get_log_unggah(limit: int = 8) -> pd.DataFrame:
    sb = get_supabase()
    if sb:
        try:
            res = (sb.table("log_unggah_data").select("jenis_unggah, nama_file, jumlah_baris, created_at")
                   .order("created_at", desc=True).limit(limit).execute())
            return pd.DataFrame(res.data or [])
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def get_alumni_summary() -> tuple[int, pd.DataFrame]:
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("v_rekap_alumni").select("*").execute()
            df = pd.DataFrame(res.data or [])
            total = int(df["total_alumni"].sum()) if not df.empty else 0
            return total, df
        except Exception:
            pass
    init_demo_state()
    return st.session_state["demo_alumni_count"], pd.DataFrame()


def upsert_siswa_aktif_3nf(df_clean: pd.DataFrame, nama_file: str, user_id: str | None = None):
    """Menyimpan data siswa aktif yang sudah tervalidasi ke skema 3NF Supabase."""
    sb = get_supabase()
    if sb:
        # 1. Master Tahun Ajaran
        ta_records = (
            df_clean[["tahun_ajaran", "tahun_mulai", "tahun_selesai"]]
            .drop_duplicates()
            .to_dict(orient="records")
        )
        sb.table("master_tahun_ajaran").upsert(ta_records).execute()

        # 2. Master Kelas
        kelas_records = []
        for _, r in df_clean[["kode_kelas", "tingkat"]].drop_duplicates().iterrows():
            kelas_records.append({
                "kode_kelas": str(r["kode_kelas"]).strip(),
                "tingkat": str(r["tingkat"]).strip(),
                "nama_rombel": f"Kelas {str(r['kode_kelas']).strip()}",
                "kapasitas": 32,
            })
        sb.table("master_kelas").upsert(kelas_records).execute()

        # 3. Master Siswa
        df_unique_siswa = df_clean.drop_duplicates(subset=["nik"]).copy()
        siswa_records = []
        for _, r in df_unique_siswa.iterrows():
            tgl = r.get("tanggal_lahir")
            tgl_val = str(tgl).strip()[:10] if pd.notna(tgl) and str(tgl).strip() and str(tgl).lower() not in ("nat", "nan", "none", "") else None
            if tgl_val and len(tgl_val) != 10:
                tgl_val = None

            nisn = r.get("nisn")
            nisn_val = str(nisn).strip() if pd.notna(nisn) and str(nisn).strip() and str(nisn).lower() not in ("nan", "none", "") else None

            siswa_records.append({
                "nik": str(r["nik"]).strip(),
                "nisn": nisn_val,
                "nama_lengkap": str(r["nama_lengkap"]).strip(),
                "jenis_kelamin": str(r["jenis_kelamin"]).strip(),
                "tempat_lahir": str(r.get("tempat_lahir", "")).strip() if pd.notna(r.get("tempat_lahir")) else "",
                "tanggal_lahir": tgl_val,
                "status_terkini": "Aktif",
            })
        
        for i in range(0, len(siswa_records), 50):
            sb.table("master_siswa").upsert(siswa_records[i:i+50]).execute()

        # 4. Riwayat Siswa Aktif
        riwayat_records = df_clean[["nik", "tahun_ajaran", "kode_kelas"]].to_dict(orient="records")
        for i in range(0, len(riwayat_records), 50):
            sb.table("riwayat_siswa_aktif").upsert(riwayat_records[i:i+50], on_conflict="nik,tahun_ajaran").execute()

        # 5. Catat Log Unggah
        sb.table("log_unggah_data").insert({
            "jenis_unggah": "Siswa Aktif",
            "nama_file": nama_file,
            "jumlah_baris": len(df_clean),
            "diunggah_oleh": user_id,
        }).execute()
    else:
        init_demo_state()
        df_old = st.session_state["demo_rekap"]
        for ta, grp in df_clean.groupby(["tahun_ajaran", "tahun_mulai"]):
            ta_str, thn_m = ta
            c7 = int((grp["tingkat"] == "VII").sum())
            c8 = int((grp["tingkat"] == "VIII").sum())
            c9 = int((grp["tingkat"] == "IX").sum())
            lk = int((grp["jenis_kelamin"] == "L").sum())
            pr = int((grp["jenis_kelamin"] == "P").sum())
            new_row = pd.DataFrame([{
                "tahun_ajaran": ta_str, "tahun_mulai": int(thn_m),
                "kelas_vii": c7, "kelas_viii": c8, "kelas_ix": c9,
                "total_aktif": c7 + c8 + c9, "total_laki": lk, "total_perempuan": pr
            }])
            df_old = pd.concat([df_old[df_old["tahun_ajaran"] != ta_str], new_row], ignore_index=True)
        st.session_state["demo_rekap"] = df_old.sort_values("tahun_mulai").reset_index(drop=True)


def upsert_alumni_3nf(df_clean: pd.DataFrame, nama_file: str, user_id: str | None = None):
    """Memindahkan status siswa menjadi Alumni & memisahkannya dari hitungan siswa aktif."""
    sb = get_supabase()
    if sb:
        ta_records = (
            df_clean[["tahun_ajaran_lulus", "tahun_mulai", "tahun_selesai"]]
            .drop_duplicates()
            .rename(columns={"tahun_ajaran_lulus": "tahun_ajaran"})
            .to_dict(orient="records")
        )
        sb.table("master_tahun_ajaran").upsert(ta_records).execute()

        df_unique_alumni = df_clean.drop_duplicates(subset=["nik"]).copy()
        siswa_records = []
        for _, r in df_unique_alumni.iterrows():
            nisn = r.get("nisn")
            nisn_val = str(nisn).strip() if pd.notna(nisn) and str(nisn).strip() and str(nisn).lower() not in ("nan", "none", "") else None
            
            siswa_records.append({
                "nik": str(r["nik"]).strip(),
                "nisn": nisn_val,
                "nama_lengkap": str(r["nama_lengkap"]).strip(),
                "jenis_kelamin": str(r["jenis_kelamin"]).strip(),
                "status_terkini": "Alumni",
            })
        
        for i in range(0, len(siswa_records), 50):
            sb.table("master_siswa").upsert(siswa_records[i:i+50]).execute()

        alumni_records = df_clean[[
            "nik", "tahun_masuk", "tahun_lulus", "tahun_ajaran_lulus", "no_ijazah", "melanjutkan_ke"
        ]].to_dict(orient="records")
        
        for i in range(0, len(alumni_records), 50):
            sb.table("riwayat_alumni").upsert(alumni_records[i:i+50]).execute()

        sb.table("log_unggah_data").insert({
            "jenis_unggah": "Alumni",
            "nama_file": nama_file,
            "jumlah_baris": len(df_clean),
            "diunggah_oleh": user_id,
        }).execute()
    else:
        init_demo_state()
        st.session_state["demo_alumni_count"] += len(df_clean)