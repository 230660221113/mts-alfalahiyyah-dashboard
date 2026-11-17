import streamlit as st

from core.auth import login
from core.config import APP_TITLE, school_name, use_supabase


def render() -> None:
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.title(APP_TITLE)
        st.caption(school_name())
        with st.form("login"):
            ident = st.text_input("Email" if use_supabase() else "Pengguna")
            pw = st.text_input("Kata sandi", type="password")
            go = st.form_submit_button("Masuk", type="primary", use_container_width=True)
        if go:
            err = login(ident, pw)
            if err:
                st.error(err)
            else:
                st.rerun()
        if not use_supabase():
            st.info("Mode demo lokal. Akun: `operator` / `pimpinan`, kata sandi `demo123`.")
