import streamlit as st

from data.repository import get_repo
from data.transform import per_class


def render() -> None:
    st.header("Kelola Data")
    repo = get_repo()
    df = repo.fetch_all()
    if df.empty:
        st.info("Belum ada data.")
        return

    st.dataframe(per_class(df).drop(columns="mulai"), hide_index=True, use_container_width=True)

    st.subheader("Hapus satu tahun ajaran")
    year = st.selectbox("Tahun ajaran", sorted(df["tahun_ajaran"].unique(), reverse=True))
    confirm = st.checkbox(f"Saya yakin ingin menghapus seluruh data {year}")
    if st.button("Hapus", disabled=not confirm):
        try:
            repo.delete_year(year)
            st.success(f"Data {year} dihapus.")
            st.rerun()
        except Exception:
            st.error("Gagal menghapus. Periksa hak akses Anda.")


render()
