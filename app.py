"""Entry point:  streamlit run app.py"""
import streamlit as st

from core.auth import current_user, logout
from core.config import APP_TITLE, school_name

st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")

user = current_user()

if user is None:
    from views import login
    login.render()
    st.stop()

pages = {
    "Analitik": [
        st.Page("views/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True),
        st.Page("views/prediksi.py", title="Prediksi", icon=":material/trending_up:"),
    ]
}
if user.is_operator:
    pages["Pengelolaan Data"] = [
        st.Page("views/unggah.py", title="Unggah Data", icon=":material/upload_file:"),
        st.Page("views/kelola.py", title="Kelola Data", icon=":material/table_rows:"),
    ]

with st.sidebar:
    st.markdown(f"**{school_name()}**")
    st.caption(f"{user.nama} · {user.role.capitalize()}")
    if st.button("Keluar", use_container_width=True):
        logout()

st.navigation(pages).run()
