import pandas as pd
import streamlit as st

from data.repository import get_repo
from data.template import build_template
from data.validation import validate


def _read(file) -> pd.DataFrame:
    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file, sheet_name=0)


def render() -> None:
    st.header("Unggah Data Siswa")
    st.download_button("Unduh templat (.xlsx)", build_template(), "template_data_siswa.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    file = st.file_uploader("Berkas data (.xlsx / .csv)", type=["xlsx", "csv"])
    if not file:
        return
    try:
        raw = _read(file)
    except Exception:
        st.error("Berkas tidak dapat dibaca. Pastikan formatnya benar.")
        return

    res = validate(raw)
    if res.errors:
        st.error(f"Ditemukan {len(res.errors)} masalah. Perbaiki lalu unggah ulang.")
        for e in res.errors[:50]:
            st.write(f"- {e}")
        return

    for w in res.warnings:
        st.warning(w)
    st.success(f"Validasi lolos: {len(res.clean)} baris siap disimpan.")
    st.dataframe(res.clean, hide_index=True, use_container_width=True)
    st.caption("Data dengan tahun ajaran dan kelas yang sama akan diperbarui.")

    if st.button("Simpan ke basis data", type="primary"):
        try:
            n = get_repo().upsert(res.clean)
            st.success(f"{n} baris tersimpan.")
        except Exception:
            st.error("Gagal menyimpan. Periksa koneksi dan hak akses Anda.")


render()
