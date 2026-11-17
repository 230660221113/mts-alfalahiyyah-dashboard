import pandas as pd
from src.validation import validate

def test_valid():
    df = pd.DataFrame([["2025/2026", "VII", "L", "Aktif", 40]], columns=["tahun_ajaran", "tingkat", "jenis_kelamin", "status", "jumlah"])
    assert validate(df) == []

def test_missing_column():
    assert "Kolom wajib" in validate(pd.DataFrame({"a": [1]}))[0]
