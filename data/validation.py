"""Validasi ketat berkas templat: deteksi & tolak spasi liar, titik koma, dan karakter tersembunyi."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

import pandas as pd

from core.constants import KELAS_VALID
from data.transform import COLUMNS, start_year

_KELAS_ALIAS = {"7": "VII", "8": "VIII", "9": "IX", "VII": "VII", "VIII": "VIII", "IX": "IX"}
_YEAR_RE = re.compile(r"^(\d{4})/(\d{4})$")
_INT_RE = re.compile(r"^\d+$")

# Karakter tersembunyi: control chars (0x00-0x1F, 0x7F-0x9F), non-breaking space (\xa0), zero-width (\u200b-\u200f, \u2060), BOM (\ufeff)
_HIDDEN_CHAR_RE = re.compile(r"[\u0000-\u001f\u007f-\u009f\u00a0\u200b-\u200f\u202a-\u202e\u2060\ufeff]")


@dataclass
class ValidationResult:
    clean: pd.DataFrame | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and self.clean is not None and not self.clean.empty


def _has_hidden_chars(val: object) -> bool:
    if pd.isna(val):
        return False
    s = str(val)
    if _HIDDEN_CHAR_RE.search(s):
        return True
    for ch in s:
        if unicodedata.category(ch) in ("Cc", "Cf", "Zl", "Zp"):
            return True
    return False


def _has_bad_whitespace_or_punct(val: object) -> list[str]:
    """Deteksi anomali teks: spasi di awal/akhir/tengah, titik koma (;), koma, tab, atau karakter tersembunyi."""
    if pd.isna(val):
        return []
    s = str(val)
    issues = []
    if _has_hidden_chars(s):
        issues.append("mengandung karakter tersembunyi/invisible Unicode (seperti non-breaking space/zero-width)")
    if ";" in s:
        issues.append("mengandung tanda titik koma (;)")
    if "," in s:
        issues.append("mengandung tanda koma (,)")
    if s != s.strip():
        issues.append("mengandung spasi berlebih di awal atau akhir teks")
    if " " in s.strip():
        issues.append("mengandung spasi di tengah nilai")
    return issues


def validate(raw: pd.DataFrame) -> ValidationResult:
    res = ValidationResult()
    if raw is None or raw.empty:
        res.errors.append("Berkas tidak berisi data.")
        return res

    # 1. Validasi ketat nama header kolom (tidak boleh ada spasi, titik koma, atau karakter tersembunyi)
    raw_cols = list(raw.columns)
    bad_headers = []
    norm_map = {}
    for col in raw_cols:
        col_str = str(col)
        issues = _has_bad_whitespace_or_punct(col_str)
        if issues:
            bad_headers.append(f"Header kolom '{repr(col_str)}' {', '.join(issues)}.")
        norm_map[col] = col_str.strip().lower()

    if bad_headers:
        res.errors.extend(bad_headers)
        res.errors.append("Gunakan header tepat tanpa spasi/titik koma: tahun_ajaran, kelas, laki_laki, perempuan.")
        return res

    df = raw.copy()
    df.columns = [norm_map[c] for c in raw_cols]
    df = df.dropna(how="all")

    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        res.errors.append(
            f"Kolom wajib tidak ditemukan: {', '.join(missing)}. Gunakan templat resmi."
        )
        return res

    extra = [c for c in df.columns if c not in COLUMNS and not c.startswith("unnamed:")]
    if extra:
        res.errors.append(
            f"Ditemukan kolom tambahan yang tidak dikenali: {', '.join(extra)}. Hapus kolom di luar templat."
        )
        return res

    df = df[COLUMNS].copy()
    if df.empty:
        res.errors.append("Berkas tidak berisi baris data.")
        return res

    df["_baris"] = df.index + 2  # baris di Excel (baris 1 = header)

    # 2. Pindai setiap sel untuk spasi liar, titik koma (;), koma, dan karakter tersembunyi
    for col in COLUMNS:
        for idx, row in df.iterrows():
            val = row[col]
            r_num = row["_baris"]
            if pd.isna(val) or str(val) == "":
                res.errors.append(f"Baris {r_num} kolom '{col}': sel tidak boleh kosong.")
                continue
            issues = _has_bad_whitespace_or_punct(val)
            if issues:
                res.errors.append(
                    f"Baris {r_num} kolom '{col}' (nilai: {repr(str(val))}): {', '.join(issues)}."
                )

    if res.errors:
        return res

    # 3. Validasi format tahun_ajaran (tepat YYYY/YYYY tanpa spasi atau pemisah lain)
    def _parse_year(v: object) -> str | None:
        s = str(v)
        m = _YEAR_RE.match(s)
        if not m:
            return None
        if int(m.group(2)) != int(m.group(1)) + 1:
            return None
        return s

    df["tahun_ajaran_clean"] = df["tahun_ajaran"].map(_parse_year)
    for r in df.loc[df["tahun_ajaran_clean"].isna(), "_baris"]:
        res.errors.append(
            f"Baris {r}: tahun_ajaran harus berformat tepat YYYY/YYYY berurutan (contoh: 2024/2025) tanpa spasi."
        )

    # 4. Validasi kelas (VII, VIII, IX atau 7, 8, 9 tanpa spasi/titik koma)
    def _parse_kelas(v: object) -> str | None:
        s = str(v).upper()
        if s.endswith(".0"):
            s = s[:-2]
        return _KELAS_ALIAS.get(s)

    df["kelas_clean"] = df["kelas"].map(_parse_kelas)
    for r in df.loc[df["kelas_clean"].isna(), "_baris"]:
        res.errors.append(
            f"Baris {r}: kelas harus salah satu dari {', '.join(KELAS_VALID)} tanpa spasi atau simbol tambahan."
        )

    # 5. Validasi bilangan bulat >= 0 pada laki_laki dan perempuan (tolak desimal/teks/simbol)
    for col in ("laki_laki", "perempuan"):
        parsed_vals = []
        for idx, row in df.iterrows():
            val = row[col]
            r_num = row["_baris"]
            s = str(val)
            if s.endswith(".0") and isinstance(val, float) and val.is_integer():
                s = str(int(val))
            if not _INT_RE.match(s):
                res.errors.append(
                    f"Baris {r_num}: {col} ('{val}') harus berupa bilangan bulat >= 0 tanpa spasi, titik, atau koma."
                )
                parsed_vals.append(None)
            else:
                parsed_vals.append(int(s))
        df[f"{col}_clean"] = parsed_vals

    if res.errors:
        return res

    # 6. Deteksi duplikasi (tahun_ajaran, kelas)
    df["tahun_ajaran"] = df["tahun_ajaran_clean"]
    df["kelas"] = df["kelas_clean"]
    df["laki_laki"] = df["laki_laki_clean"].astype(int)
    df["perempuan"] = df["perempuan_clean"].astype(int)

    dup = df.duplicated(["tahun_ajaran", "kelas"], keep=False)
    for (t, k), grp in df[dup].groupby(["tahun_ajaran", "kelas"]):
        rows = ", ".join(map(str, grp["_baris"]))
        res.errors.append(f"Data ganda untuk {t} kelas {k} ditemukan pada baris {rows}.")

    if res.errors:
        return res

    clean = df[COLUMNS].sort_values(["tahun_ajaran", "kelas"]).reset_index(drop=True)

    # 7. Peringatan non-blocking (kelengkapan kelas & kontinuitas tahun ajaran)
    for t, grp in clean.groupby("tahun_ajaran"):
        absent = set(KELAS_VALID) - set(grp["kelas"])
        if absent:
            res.warnings.append(
                f"Tahun ajaran {t}: kelas {', '.join(sorted(absent))} belum ada, total tahun ini belum lengkap."
            )
    years = sorted(start_year(t) for t in clean["tahun_ajaran"].unique())
    if len(years) > 1:
        gaps = sorted(set(range(years[0], years[-1] + 1)) - set(years))
        if gaps:
            res.warnings.append(
                "Terdapat tahun ajaran yang terlewat: " + ", ".join(f"{g}/{g + 1}" for g in gaps)
            )

    res.clean = clean
    return res
