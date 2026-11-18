import re
import pandas as pd

NIK_REGEX = re.compile(r"^\d{16}$")
NISN_REGEX = re.compile(r"^\d{10}$")
TA_REGEX = re.compile(r"^(\d{4})/(\d{4})$")


def _clean_raw_id(val) -> str:
    """Mengubah nilai sel Excel menjadi string mentah tanpa menghilangkan tanda titik/anomali untuk deteksi."""
    if pd.isna(val):
        return ""
    s = str(val).strip()
    # Tangani kasus Excel membaca angka besar sebagai float berakhiran .0
    if re.match(r"^\d+\.0$", s):
        s = s[:-2]
    return s


def validate_siswa_aktif_df(df: pd.DataFrame) -> tuple[bool, list[str], pd.DataFrame]:
    """
    Memvalidasi & menormalisasi DataFrame Unggah Data Siswa Aktif (format EMIS).
    Mengembalikan: (is_valid, daftar_peringatan, df_bersih)
    """
    errors: list[str] = []
    required_cols = [
        "NIK", "NISN", "Nama_Lengkap", "Jenis_Kelamin",
        "Tahun_Ajaran", "Tingkat_Kelas", "Rombel"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        return False, [f"Kolom wajib tidak ditemukan pada file Excel: {', '.join(missing)}. Gunakan templat resmi Data Siswa Aktif."], df

    if df.empty:
        return False, ["File Excel kosong (tidak ada baris data siswa)."], df

    clean_rows = []
    seen_nik = set()

    for idx, row in df.iterrows():
        baris_excel = idx + 2
        raw_nik = _clean_raw_id(row.get("NIK"))
        raw_nisn = _clean_raw_id(row.get("NISN"))
        nama = str(row.get("Nama_Lengkap", "")).strip() if not pd.isna(row.get("Nama_Lengkap")) else ""
        jk = str(row.get("Jenis_Kelamin", "")).strip().upper() if not pd.isna(row.get("Jenis_Kelamin")) else ""
        ta = str(row.get("Tahun_Ajaran", "")).strip() if not pd.isna(row.get("Tahun_Ajaran")) else ""
        tingkat = str(row.get("Tingkat_Kelas", "")).strip().upper() if not pd.isna(row.get("Tingkat_Kelas")) else ""
        rombel = str(row.get("Rombel", "")).strip().upper() if not pd.isna(row.get("Rombel")) else ""
        tempat_lahir = str(row.get("Tempat_Lahir", "")).strip() if not pd.isna(row.get("Tempat_Lahir")) else ""
        tgl_lahir = str(row.get("Tanggal_Lahir", "")).strip()[:10] if not pd.isna(row.get("Tanggal_Lahir")) else None

        # 1. Validasi ketat NIK (deteksi titik, spasi, huruf, atau panjang != 16)
        if not raw_nik:
            errors.append(f"Baris {baris_excel} ({nama or 'Tanpa Nama'}): NIK kosong.")
            continue
        if "." in raw_nik or "," in raw_nik or " " in raw_nik or "-" in raw_nik:
            errors.append(
                f"Baris {baris_excel} ({nama}): NIK '{raw_nik}' mengandung tanda baca/spasi (seperti titik). "
                "NIK wajib 16 digit angka murni."
            )
            continue
        if not NIK_REGEX.match(raw_nik):
            errors.append(
                f"Baris {baris_excel} ({nama}): NIK '{raw_nik}' tidak valid (terbaca {len(raw_nik)} karakter, wajib tepat 16 digit angka)."
            )
            continue
        if raw_nik in seen_nik:
            errors.append(f"Baris {baris_excel} ({nama}): Duplikasi NIK '{raw_nik}' ditemukan di dalam file yang sama.")
            continue
        seen_nik.add(raw_nik)

        # 2. Validasi ketat NISN (opsional jika kosong, namun jika diisi wajib 10 digit angka murni tanpa titik)
        if raw_nisn:
            if "." in raw_nisn or " " in raw_nisn or not NISN_REGEX.match(raw_nisn):
                errors.append(
                    f"Baris {baris_excel} ({nama}): NISN '{raw_nisn}' tidak valid (mengandung titik/spasi atau bukan 10 digit angka)."
                )
                continue

        # 3. Validasi Nama, JK, Tahun Ajaran, Tingkat Kelas
        if len(nama) < 2:
            errors.append(f"Baris {baris_excel} (NIK {raw_nik}): Nama_Lengkap wajib diisi.")
            continue
        if jk not in ("L", "P"):
            errors.append(f"Baris {baris_excel} ({nama}): Jenis_Kelamin '{jk}' tidak valid (gunakan 'L' atau 'P').")
            continue
        m_ta = TA_REGEX.match(ta)
        if not m_ta or int(m_ta.group(2)) != int(m_ta.group(1)) + 1:
            errors.append(f"Baris {baris_excel} ({nama}): Tahun_Ajaran '{ta}' tidak valid (gunakan format YYYY/YYYY, contoh 2025/2026).")
            continue
        if tingkat not in ("VII", "VIII", "IX"):
            errors.append(f"Baris {baris_excel} ({nama}): Tingkat_Kelas '{tingkat}' tidak valid (wajib VII, VIII, atau IX).")
            continue
        if not rombel:
            rombel = f"{tingkat}-A"

        clean_rows.append({
            "nik": raw_nik,
            "nisn": raw_nisn if raw_nisn else None,
            "nama_lengkap": nama,
            "jenis_kelamin": jk,
            "tempat_lahir": tempat_lahir,
            "tanggal_lahir": tgl_lahir if tgl_lahir else None,
            "tahun_ajaran": ta,
            "tahun_mulai": int(m_ta.group(1)),
            "tahun_selesai": int(m_ta.group(2)),
            "tingkat": tingkat,
            "kode_kelas": rombel,
        })

    return (len(errors) == 0), errors, pd.DataFrame(clean_rows)


def validate_alumni_df(df: pd.DataFrame) -> tuple[bool, list[str], pd.DataFrame]:
    """
    Memvalidasi & menormalisasi DataFrame Unggah Data Alumni (Lulusan).
    """
    errors: list[str] = []
    required_cols = ["NIK", "Nama_Lengkap", "Jenis_Kelamin", "Tahun_Lulus", "Tahun_Ajaran_Lulus"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        return False, [f"Kolom wajib tidak ditemukan pada file Alumni: {', '.join(missing)}. Gunakan templat resmi Data Alumni."], df

    if df.empty:
        return False, ["File Excel Alumni kosong."], df

    clean_rows = []
    seen_nik = set()

    for idx, row in df.iterrows():
        baris_excel = idx + 2
        raw_nik = _clean_raw_id(row.get("NIK"))
        raw_nisn = _clean_raw_id(row.get("NISN"))
        nama = str(row.get("Nama_Lengkap", "")).strip() if not pd.isna(row.get("Nama_Lengkap")) else ""
        jk = str(row.get("Jenis_Kelamin", "")).strip().upper() if not pd.isna(row.get("Jenis_Kelamin")) else ""
        ta_lulus = str(row.get("Tahun_Ajaran_Lulus", "")).strip() if not pd.isna(row.get("Tahun_Ajaran_Lulus")) else ""
        thn_lulus_raw = _clean_raw_id(row.get("Tahun_Lulus"))
        thn_masuk_raw = _clean_raw_id(row.get("Tahun_Masuk"))
        no_ijazah = str(row.get("No_Ijazah", "")).strip() if not pd.isna(row.get("No_Ijazah")) else ""
        lanjut = str(row.get("Melanjutkan_Ke", "")).strip() if not pd.isna(row.get("Melanjutkan_Ke")) else ""

        if "." in raw_nik or "," in raw_nik or " " in raw_nik or not NIK_REGEX.match(raw_nik):
            errors.append(
                f"Baris {baris_excel} ({nama or 'Tanpa Nama'}): NIK '{raw_nik}' tidak valid (terdeteksi titik/spasi atau bukan 16 digit angka)."
            )
            continue
        if raw_nik in seen_nik:
            errors.append(f"Baris {baris_excel} ({nama}): Duplikasi NIK '{raw_nik}' di dalam file Alumni.")
            continue
        seen_nik.add(raw_nik)

        if raw_nisn and ("." in raw_nisn or not NISN_REGEX.match(raw_nisn)):
            errors.append(f"Baris {baris_excel} ({nama}): NISN '{raw_nisn}' tidak valid (wajib 10 digit angka murni).")
            continue
        if jk not in ("L", "P"):
            errors.append(f"Baris {baris_excel} ({nama}): Jenis_Kelamin '{jk}' wajib 'L' atau 'P'.")
            continue
        if not thn_lulus_raw.isdigit() or len(thn_lulus_raw) != 4:
            errors.append(f"Baris {baris_excel} ({nama}): Tahun_Lulus '{thn_lulus_raw}' wajib 4 digit tahun (contoh: 2025).")
            continue
        m_ta = TA_REGEX.match(ta_lulus)
        if not m_ta or int(m_ta.group(2)) != int(m_ta.group(1)) + 1:
            errors.append(f"Baris {baris_excel} ({nama}): Tahun_Ajaran_Lulus '{ta_lulus}' wajib format YYYY/YYYY.")
            continue

        clean_rows.append({
            "nik": raw_nik,
            "nisn": raw_nisn if raw_nisn else None,
            "nama_lengkap": nama,
            "jenis_kelamin": jk,
            "tahun_masuk": int(thn_masuk_raw) if thn_masuk_raw.isdigit() else None,
            "tahun_lulus": int(thn_lulus_raw),
            "tahun_ajaran_lulus": ta_lulus,
            "tahun_mulai": int(m_ta.group(1)),
            "tahun_selesai": int(m_ta.group(2)),
            "no_ijazah": no_ijazah,
            "melanjutkan_ke": lanjut,
        })

    return (len(errors) == 0), errors, pd.DataFrame(clean_rows)
