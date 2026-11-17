import streamlit as st

from core.auth import login
from core.config import APP_TITLE, school_name, use_supabase


def render() -> None:
    st.markdown("<div style='height: 3.5rem;'></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.15, 1])
    with mid:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="login-header">
                    <div class="login-logo">🎓</div>
                    <h2 style="margin:0; font-weight:800; color:#0F172A; font-size:1.55rem;">{APP_TITLE}</h2>
                    <p style="margin:0.3rem 0 0 0; color:#64748B; font-size:0.9rem;">{school_name()} · Kabupaten Sumedang</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.form("login"):
                ident = st.text_input(
                    "Email" if use_supabase() else "Nama Pengguna",
                    placeholder="Masukkan email atau username...",
                )
                pw = st.text_input(
                    "Kata Sandi",
                    type="password",
                    placeholder="Masukkan kata sandi...",
                )
                st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)
                go = st.form_submit_button("Masuk ke Dashboard", type="primary", use_container_width=True)
            if go:
                err = login(ident, pw)
                if err:
                    st.error(err)
                else:
                    st.rerun()

        if not use_supabase():
            st.info("💡 **Mode Demo Lokal:** Gunakan akun `operator` atau `pimpinan` dengan kata sandi `demo123`.")
