"""Entry point: streamlit run app.py"""
import streamlit as st

from core.auth import current_user, logout
from core.config import APP_TITLE, school_name
from ui.styles import inject_global_css

st.set_page_config(
    page_title=f"{APP_TITLE} — {school_name()}",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css()

user = current_user()

if user is None:
    from views import login
    login.render()
    st.stop()

pages = {
    "Analitik & Peramalan": [
        st.Page("views/dashboard.py", title="Dashboard Utama", icon=":material/dashboard:", default=True),
        st.Page("views/prediksi.py", title="Prediksi Siswa", icon=":material/trending_up:"),
    ]
}
if user.is_operator:
    pages["Pengelolaan Data"] = [
        st.Page("views/unggah.py", title="Unggah Data", icon=":material/upload_file:"),
        st.Page("views/kelola.py", title="Kelola Data", icon=":material/table_rows:"),
    ]

with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-profile">
            <div class="sidebar-school">🏫 {school_name()}</div>
            <div class="sidebar-role">👤 {user.nama} · <b>{user.role.capitalize()}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Keluar dari Sistem", icon=":material/logout:", use_container_width=True):
        logout()

st.navigation(pages).run()
