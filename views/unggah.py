import pandas as pd
import streamlit as st

from core.config import school_name
from data.repository import get_repo
from data.template import build_template
from data.validation import validate
from ui.styles import render_hero


def _read(file) -> pd.DataFrame:
    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file, sheet_name=0)


def render() -> None:
    render_hero(
        title="Unggah Data Kesiswaan",
        subtitle=f"Impor berkas spreadsheet terstandar (.xlsx / .csv) ke basis data terpusat {school_name()}.",
        badge_text="📤 Validasi Otomatis Aktif",
    )

    with st.container(border=True):
        st.markdown('<div class="chart-title">1. Unduh Templat & Unggah Berkas</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-subtitle">Gunakan format kolom resmi: <code>tahun_ajaran</code>, <code>kelas</code> (VII/VIII/IX), <code>laki_laki</code>, dan <code>perempuan</code>.</div>',
            unsafe_allow_html=True,
        )
        st.download_button(
            "Unduh Templat Resmi (.xlsx)",
            build_template(),
            "template_data_siswa.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            icon=":material/download:",
        )
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        file = st.file_uploader("Pilih berkas data (.xlsx atau .csv)", type=["xlsx", "csv"])

    if not file:
        return

    try:
        raw = _read(file)
    except Exception:
        st.error("Berkas tidak dapat dibaca. Pastikan format file tidak rusak.")
        return

    res = validate(raw)
    if res.errors:
        with st.container(border=True):
            st.error(f"Ditemukan **{len(res.errors)} masalah** validasi. Perbaiki berkas Anda lalu unggah ulang.")
            for e in res.errors[:50]:
                st.write(f"- {e}")
        return

    with st.container(border=True):
        st.markdown('<div class="chart-title">2. Pratinjau & Simpan ke Basis Data</div>', unsafe_allow_html=True)
        for w in res.warnings:
            st.warning(w)
        st.success(f"Validasi berhasil: **{len(res.clean)} baris** siap disimpan ke basis data.")
        st.dataframe(res.clean, hide_index=True, use_container_width=True)
        st.caption("Catatan: Data dengan kombinasi tahun ajaran dan kelas yang sudah ada akan otomatis diperbarui (upsert).")

        if st.button("Simpan ke Basis Data", type="primary", icon=":material/save:"):
            try:
                n = get_repo().upsert(res.clean)
                st.success(f"Berhasil menyimpan **{n} baris** ke basis data.")
            except Exception:
                st.error("Gagal menyimpan data. Periksa koneksi basis data dan hak akses Anda.")


render()
