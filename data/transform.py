"""Transformasi data rekap siswa -> bentuk yang siap divisualisasikan/diprediksi."""
from __future__ import annotations

import pandas as pd

COLUMNS = ["tahun_ajaran", "kelas", "laki_laki", "perempuan"]


def empty_frame() -> pd.DataFrame:
    return pd.DataFrame({c: pd.Series(dtype="object" if c in ("tahun_ajaran", "kelas") else "int64")
                         for c in COLUMNS})


def start_year(label: str) -> int:
    return int(str(label).split("/")[0])


def year_label(start: int) -> str:
    return f"{start}/{start + 1}"


def with_total(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["total"] = out["laki_laki"] + out["perempuan"]
    return out


def yearly_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Satu baris per tahun ajaran: laki_laki, perempuan, total, mulai (tahun awal)."""
    if df.empty:
        return pd.DataFrame(columns=["tahun_ajaran", "laki_laki", "perempuan", "total", "mulai"])
    g = df.groupby("tahun_ajaran", as_index=False)[["laki_laki", "perempuan"]].sum()
    g["total"] = g["laki_laki"] + g["perempuan"]
    g["mulai"] = g["tahun_ajaran"].map(start_year)
    return g.sort_values("mulai").reset_index(drop=True)


def per_class(df: pd.DataFrame) -> pd.DataFrame:
    out = with_total(df)
    out["mulai"] = out["tahun_ajaran"].map(start_year)
    return out.sort_values(["mulai", "kelas"]).reset_index(drop=True)
