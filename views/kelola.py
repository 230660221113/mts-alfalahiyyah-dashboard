import streamlit as st

from core.config import school_name
from data.repository import get_repo
from data.transform import per_class
from ui.styles import render_hero


def render() -> None:
    repo = get_repo()
    df = repo.fetch_all()

    render_hero(
        title="Kelola Data Tersimpan",
        subtitle=f"Tinjau rekapitulasi data kesiswaan per kelas yang tersimpan di basis data {school_name()}.",
        badge_text=f"🗄️ Total Record: {len(df)} Baris",
    )

    if df.empty:
        st.info("Belum ada data tersimpan di basis data.")
        return

    with st.container(border=True):
        st.markdown('<div class="chart-title">Daftar Rekapitulasi Per Kelas</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-subtitle">Seluruh data historis yang aktif digunakan pada visualisasi dan pemodelan</div>', unsafe_allow_html=True)
        display_df = per_class(df).drop(columns="mulai").rename(
            columns={
                "tahun_ajaran": "Tahun Ajaran",
                "kelas": "Kelas",
                "laki_laki": "Laki-laki",
                "perempuan": "Perempuan",
                "total": "Total Siswa",
            }
        )
        st.dataframe(display_df, hide_index=True, use_container_width=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="chart-title">Hapus Data Tahun Ajaran</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-subtitle">Gunakan fitur ini untuk membersihkan data uji coba atau memperbarui tahun ajaran tertentu</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        year = c1.selectbox("Pilih Tahun Ajaran", sorted(df["tahun_ajaran"].unique(), reverse=True))
        confirm = st.checkbox(f"Saya yakin ingin menghapus seluruh data kesiswaan tahun ajaran {year}")
        if st.button("Hapus Data Tahun Ajaran", disabled=not confirm, icon=":material/delete:"):
            try:
                repo.delete_year(year)
                st.success(f"Seluruh data tahun ajaran **{year}** berhasil dihapus.")
                st.rerun()
            except Exception:
                st.error("Gagal menghapus data. Periksa hak akses Anda.")


render()
