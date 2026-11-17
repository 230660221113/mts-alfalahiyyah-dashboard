import pandas as pd
from data.validation import validate

def df(rows): return pd.DataFrame(rows, columns=["tahun_ajaran", "kelas", "laki_laki", "perempuan"])

def test_valid_and_alias():
    r = validate(df([["2024/2025", 7, 10, 12], ["2024/2025", "viii", 9, 8]]))
    assert r.ok and list(r.clean["kelas"]) == ["VII", "VIII"]

def test_bad_year_class_number():
    r = validate(df([["2024-2025", "X", -1, 2.5]]))
    assert len(r.errors) == 4

def test_duplicate():
    r = validate(df([["2024/2025", "VII", 1, 1], ["2024/2025", "VII", 2, 2]]))
    assert any("ganda" in e for e in r.errors)

def test_missing_column():
    r = validate(pd.DataFrame({"a": [1]}))
    assert not r.ok and "Kolom wajib" in r.errors[0]

def test_gap_warning():
    rows = [[f"{y}/{y+1}", k, 1, 1] for y in (2020, 2022) for k in ("VII", "VIII", "IX")]
    assert any("terlewat" in w for w in validate(df(rows)).warnings)
