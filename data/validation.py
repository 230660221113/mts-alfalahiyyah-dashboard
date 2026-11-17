"""Validasi otomatis berkas template yang diunggah operator."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

from core.constants import KELAS_VALID
from data.transform import COLUMNS, start_year

_KELAS_ALIAS = {"7": "VII", "8": "VIII", "9": "IX", "VII": "VII", "VIII": "VIII", "IX": "IX"}
_YEAR_RE = re.compile(r"^\s*(\d{4})\s*/\s*(\d{4})\s*$")


@dataclass
class ValidationResult:
    clean: pd.DataFrame | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and self.clean is not None and not self.clean.empty


def _norm_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df


def validate(raw: pd.DataFrame) -> ValidationResult:
    res = ValidationResult()
    df = _norm_cols(raw).dropna(how="all")

    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        res.errors.append(f"Kolom wajib tidak ditemukan: {', '.join(missing)}. "
                          "Gunakan templat resmi.")
        return res
    df = df[COLUMNS].copy()
    if df.empty:
        res.errors.append("Berkas tidak berisi data.")
        return res

    df["_baris"] = df.index + 2  # baris di Excel (header = baris 1)

    # --- tahun ajaran
    def _year(v):
        m = _YEAR_RE.match(str(v))
        if not m or int(m.group(2)) != int(m.group(1)) + 1:
            return None
        return f"{m.group(1)}/{m.group(2)}"

    df["tahun_ajaran"] = df["tahun_ajaran"].map(_year)
    for r in df.loc[df["tahun_ajaran"].isna(), "_baris"]:
        res.errors.append(f"Baris {r}: tahun_ajaran harus berformat 2024/2025 (tahun berurutan).")

    # --- kelas
    df["kelas"] = df["kelas"].map(lambda v: _KELAS_ALIAS.get(str(v).strip().upper().removesuffix(".0")))
    for r in df.loc[df["kelas"].isna(), "_baris"]:
        res.errors.append(f"Baris {r}: kelas harus salah satu dari {', '.join(KELAS_VALID)}.")

    # --- angka
    for col in ("laki_laki", "perempuan"):
        num = pd.to_numeric(df[col], errors="coerce")
        bad = num.isna() | (num < 0) | (num % 1 != 0)
        for r in df.loc[bad, "_baris"]:
            res.errors.append(f"Baris {r}: {col} harus bilangan bulat >= 0.")
        df[col] = num

    # --- duplikat
    ok_rows = df.dropna(subset=["tahun_ajaran", "kelas"])
    dup = ok_rows.duplicated(["tahun_ajaran", "kelas"], keep=False)
    for (t, k), grp in ok_rows[dup].groupby(["tahun_ajaran", "kelas"]):
        rows = ", ".join(map(str, grp["_baris"]))
        res.errors.append(f"Data ganda untuk {t} kelas {k} (baris {rows}).")

    if res.errors:
        return res

    clean = df.drop(columns="_baris")
    clean[["laki_laki", "perempuan"]] = clean[["laki_laki", "perempuan"]].astype(int)
    clean = clean.sort_values(["tahun_ajaran", "kelas"]).reset_index(drop=True)

    # --- peringatan (tidak menggagalkan unggahan)
    for t, grp in clean.groupby("tahun_ajaran"):
        absent = set(KELAS_VALID) - set(grp["kelas"])
        if absent:
            res.warnings.append(f"{t}: kelas {', '.join(sorted(absent))} tidak ada, total tahun ini bisa tidak lengkap.")
    years = sorted(start_year(t) for t in clean["tahun_ajaran"].unique())
    gaps = sorted(set(range(years[0], years[-1] + 1)) - set(years))
    if gaps:
        res.warnings.append("Tahun ajaran terlewat: " + ", ".join(f"{g}/{g + 1}" for g in gaps))

    res.clean = clean
    return res
