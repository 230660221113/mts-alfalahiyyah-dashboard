import pandas as pd
import streamlit as st

TINGKAT = ["VII", "VIII", "IX"]

def _demo() -> pd.DataFrame:
    """DATA CONTOH untuk pratinjau desain. Ganti dengan data dari Supabase."""
    base = {"VII": [62, 66, 70, 68, 74, 80, 78, 85], "VIII": [58, 60, 65, 68, 66, 72, 79, 77], "IX": [55, 57, 59, 64, 67, 65, 71, 78]}
    years = [f"{y}/{y+1}" for y in range(2018, 2026)]
    rows = []
    for t, vals in base.items():
        for y, v in zip(years, vals):
            l = round(v * 0.52)
            rows += [(y, t, "L", "Aktif", l), (y, t, "P", "Aktif", v - l)]
    return pd.DataFrame(rows, columns=["tahun_ajaran", "tingkat", "jenis_kelamin", "status", "jumlah"])

def load() -> pd.DataFrame:
    if "data" not in st.session_state:
        st.session_state["data"] = _demo()   # TODO: query tabel Supabase
        st.session_state["is_demo"] = True
    return st.session_state["data"]

def template_xlsx() -> bytes:
    from io import BytesIO
    ex = pd.DataFrame([["2025/2026", "VII", "L", "Aktif", 40]], columns=["tahun_ajaran", "tingkat", "jenis_kelamin", "status", "jumlah"])
    buf = BytesIO()
    ex.to_excel(buf, index=False)
    return buf.getvalue()
