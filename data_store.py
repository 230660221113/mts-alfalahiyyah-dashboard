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
    if "demo_users" not in st.session_state:
        st.session_state["demo_users"] = {
            "operator@alfalahiyyah.sch.id": {"password": "operator123", "nama": "Operator MTs", "jabatan": "Operator", "role": "operator", "aktif": True},
            "kepsek@alfalahiyyah.sch.id": {"password": "kepsek123", "nama": "Kepala Madrasah", "jabatan": "Kepala", "role": "kepala_sekolah", "aktif": True},
        }
    if "demo_settings" not in st.session_state:
        st.session_state["demo_settings"] = {"nama_madrasah": "MTs Al-Falahiyyah", "wa_operator": "6281234567890", "kapasitas_rombel": "32", "rasio_guru_siswa": "20"}
    if "demo_rekap" not in st.session_state:
        st.session_state["demo_rekap"] = pd.DataFrame()
    if "demo_alumni_count" not in st.session_state:
        st.session_state["demo_alumni_count"] = 0


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
                "kode_kelas": r["kode_kelas"],
                "tingkat": r["tingkat"],
                "nama_rombel": f"Kelas {r['kode_kelas']}",
            })
        sb.table("master_kelas").upsert(kelas_records).execute()

        # 3. Master Siswa (Pembersihan aman untuk tanggal & NISN kosong)
        siswa_records = []
        for _, r in df_clean.drop_duplicates(subset=["nik"]).iterrows():
            tgl = r.get("tanggal_lahir")
            tgl_val = str(tgl).strip()[:10] if pd.notna(tgl) and str(tgl).strip() and str(tgl).lower() not in ("nat", "nan", "none", "") else None
            if tgl_val and len(tgl_val) != 10:
                tgl_val = None

            nisn = r.get("nisn")
            nisn_val = str(nisn).strip() if pd.notna(nisn) and str(nisn).strip() and str(nisn).lower() != "nan" else None

            siswa_records.append({
                "nik": str(r["nik"]).strip(),
                "nisn": nisn_val,
                "nama_lengkap": str(r["nama_lengkap"]).strip(),
                "jenis_kelamin": str(r["jenis_kelamin"]).strip(),
                "tempat_lahir": str(r.get("tempat_lahir", "")).strip() if pd.notna(r.get("tempat_lahir")) else "",
                "tanggal_lahir": tgl_val,
                "status_terkini": "Aktif",
            })
        
        # Eksekusi upsert ke tabel master_siswa per batch kecil untuk menghindari limit payload
        for i in range(0, len(siswa_records), 50):
            batch = siswa_records[i:i+50]
            sb.table("master_siswa").upsert(batch).execute()

        # 4. Riwayat Siswa Aktif (Batching juga)
        riwayat_records = df_clean[["nik", "tahun_ajaran", "kode_kelas"]].to_dict(orient="records")
        for i in range(0, len(riwayat_records), 50):
            batch = riwayat_records[i:i+50]
            sb.table("riwayat_siswa_aktif").upsert(batch, on_conflict="nik,tahun_ajaran").execute()

        # 5. Catat Log Unggah
        sb.table("log_unggah_data").insert({
            "jenis_unggah": "Siswa Aktif",
            "nama_file": nama_file,
            "jumlah_baris": len(df_clean),
            "diunggah_oleh": user_id,
        }).execute()
    else:
        init_demo_state()
        # Fallback lokal jika demo
        pass


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

        siswa_records = []
        for _, r in df_clean.drop_duplicates(subset=["nik"]).iterrows():
            nisn = r.get("nisn")
            nisn_val = str(nisn).strip() if pd.notna(nisn) and str(nisn).strip() and str(nisn).lower() != "nan" else None
            
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