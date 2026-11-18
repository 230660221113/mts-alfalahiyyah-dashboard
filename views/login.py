import streamlit as st

from core.auth import login, request_password_reset
from core.config import APP_TITLE, school_name, use_supabase


def render() -> None:
    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.25, 1])
    with mid:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="login-header">
                    <div class="login-logo">🎓</div>
                    <h2 style="margin:0; font-weight:800; color:#0F172A; font-size:1.5rem;">{APP_TITLE}</h2>
                    <p style="margin:0.3rem 0 0 0; color:#64748B; font-size:0.9rem;">{school_name()} · Kabupaten Sumedang</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            tab_login, tab_forgot = st.tabs(["🔑 Masuk Sistem", "🔄 Lupa Kata Sandi"])

            with tab_login:
                with st.form("login_form"):
                    ident = st.text_input(
                        "Email" if use_supabase() else "Username atau Email",
                        placeholder="Masukkan email atau username...",
                    )
                    pw = st.text_input(
                        "Kata Sandi",
                        type="password",
                        placeholder="Masukkan kata sandi...",
                    )
                    st.markdown("<div style='height: 0.3rem;'></div>", unsafe_allow_html=True)
                    go = st.form_submit_button("Masuk ke Dashboard", type="primary", use_container_width=True)
                if go:
                    err = login(ident, pw)
                    if err:
                        st.error(err)
                    else:
                        st.rerun()

            with tab_forgot:
                if use_supabase():
                    st.caption("Masukkan alamat email terdaftar untuk menerima tautan pengaturan ulang kata sandi.")
                    with st.form("forgot_sb_form"):
                        email_reset = st.text_input("Email Terdaftar", placeholder="nama@alfalahiyyah.sch.id")
                        send_reset = st.form_submit_button("Kirim Tautan Reset Kata Sandi", type="primary", use_container_width=True)
                    if send_reset:
                        ok, msg = request_password_reset(email_reset)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
                else:
                    st.caption("Atur ulang kata sandi menggunakan kode pemulihan madrasah (atau hubungi Operator Super Admin).")
                    with st.form("forgot_local_form"):
                        ident_reset = st.text_input("Username atau Email", placeholder="operator atau kepsek")
                        rec_code = st.text_input("Kode Pemulihan Madrasah", type="password", placeholder="Default: ALFALAHIYYAH2026")
                        new_pw1 = st.text_input("Kata Sandi Baru (min. 6 karakter)", type="password")
                        new_pw2 = st.text_input("Konfirmasi Kata Sandi Baru", type="password")
                        do_reset = st.form_submit_button("Simpan Kata Sandi Baru", type="primary", use_container_width=True)
                    if do_reset:
                        if new_pw1 != new_pw2:
                            st.error("Konfirmasi kata sandi baru tidak cocok.")
                        else:
                            ok, msg = request_password_reset(ident_reset, new_pw1, rec_code)
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)

        if not use_supabase():
            st.info(
                "💡 **Mode Demo Lokal:** Akun `operator` (Super Admin) & `kepsek` (Kepala Sekolah) · "
                "Kata sandi default: `demo123`"
            )
