import pandas as pd
import streamlit as st

from core.config import school_name
from data.repository import get_repo
from data.template import build_template
from data.validation import validate
from ui.styles import render_hero


def _read(file) -> tuple[pd.DataFrame, str | None]:
    """Membaca berkas Excel/CSV sebagai string mentah (dtype=str) agar spasi/karakter tersembunyi tidak hilang."""
    name = file.name.lower()
    if name.endswith(".csv"):
        raw_bytes = file.getvalue()
        text_preview = raw_bytes.decode("utf-8-sig", errors="replace")
        first_line = text_preview.splitlines()[0] if text_preview.splitlines() else ""
        if ";" in first_line:
            return pd.DataFrame(), (
                "Format CSV menggunakan pemisah titik koma (;). "
                "Simpan ulang berkas sebagai Excel (.xlsx) menggunakan templat resmi atau CSV pemisah koma (,)."
            )
        file.seek(0)
        return pd.read_csv(file, dtype=str, keep_default_na=False), None

    return pd.read_excel(file, sheet_name=0, dtype=str, keep_default_na=False), None


def render() -> None:
    render_hero(
        title="Unggah Data Kesiswaan",
        subtitle=f"Impor berkas spreadsheet terstandar (.xlsx / .csv) ke basis data terpusat {school_name()}.",
        badge_text="🛡️ Hak Akses: Operator (Super Admin)",
    )

    with st.container(border=True):
        st.markdown('<div class="chart-title">1. Unduh Templat & Unggah Berkas</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-subtitle">Sistem memeriksa integritas format secara ketat: menolak spasi berlebih, tanda titik koma (<code>;</code>), koma, maupun karakter tersembunyi Unicode.</div>',
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
        raw, read_err = _read(file)
    except Exception:
        st.error("Berkas tidak dapat dibaca. Pastikan format file Excel/CSV tidak rusak.")
        return

    if read_err:
        with st.container(border=True):
            st.error(read_err)
        return

    res = validate(raw)
    if res.errors:
        with st.container(border=True):
            st.error(
                f"Ditemukan **{len(res.errors)} masalah format/anomali teks**. "
                "Perbaiki sel yang bermasalah pada berkas Anda lalu unggah ulang:"
            )
            for e in res.errors[:50]:
                st.write(f"- {e}")
        return

    with st.container(border=True):
        st.markdown('<div class="chart-title">2. Pratinjau & Simpan ke Basis Data</div>', unsafe_allow_html=True)
        for w in res.warnings:
            st.warning(w)
        st.success(f"Validasi ketat lolos: **{len(res.clean)} baris** bersih dan siap disimpan.")
        st.dataframe(res.clean, hide_index=True, use_container_width=True)
        st.caption("Catatan: Data dengan kombinasi tahun ajaran dan kelas yang sama akan otomatis diperbarui (upsert).")

        if st.button("Simpan ke Basis Data", type="primary", icon=":material/save:"):
            try:
                n = get_repo().upsert(res.clean)
                st.success(f"Berhasil menyimpan **{n} baris** ke basis data.")
            except Exception:
                st.error("Gagal menyimpan data. Periksa koneksi basis data dan hak akses Anda.")


render()
