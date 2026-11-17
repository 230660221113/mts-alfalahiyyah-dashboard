import pandas as pd

REQUIRED = ["tahun_ajaran", "tingkat", "jenis_kelamin", "status", "jumlah"]

def validate(df: pd.DataFrame) -> list[str]:
    """Kembalikan daftar pesan kesalahan. Kosong = lolos."""
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        return [f"Kolom wajib tidak ditemukan: {', '.join(missing)}"]
    errs = []
    for i, r in df.iterrows():
        n = i + 2  # baris Excel (header = baris 1)
        if pd.isna(r[REQUIRED]).any():
            errs.append(f"Baris {n}: ada kolom yang kosong.")
            continue
        if r["tingkat"] not in ("VII", "VIII", "IX"):
            errs.append(f"Baris {n}: tingkat harus VII, VIII, atau IX.")
        if r["jenis_kelamin"] not in ("L", "P"):
            errs.append(f"Baris {n}: jenis kelamin harus L atau P.")
        if not str(r["jumlah"]).isdigit():
            errs.append(f"Baris {n}: jumlah harus bilangan bulat ≥ 0.")
    dup = df.duplicated(["tahun_ajaran", "tingkat", "jenis_kelamin", "status"], keep=False)
    if dup.any():
        errs.append(f"Ada kombinasi data ganda di baris: {', '.join(str(i + 2) for i in df.index[dup])}.")
    return errs
