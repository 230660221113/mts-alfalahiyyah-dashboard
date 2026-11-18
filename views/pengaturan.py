import streamlit as st

from core.auth import (
    LocalAccountStore,
    change_current_password,
    current_user,
    update_current_profile,
)
from core.config import role_label, school_name, use_supabase
from ui.styles import render_hero


def render() -> None:
    user = current_user()
    if not user:
        st.warning("Silakan masuk terlebih dahulu.")
        return

    render_hero(
        title="Pengaturan Akun & Keamanan",
        subtitle=f"Kelola informasi profil, username, dan kata sandi pengguna pada sistem {school_name()}.",
        badge_text=f"👤 {user.display_role}",
    )

    col_left, col_right = st.columns(2)

    # Kartu 1: Ubah Profil & Username
    with col_left:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Profil & Username Pengguna</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="chart-subtitle">Perbarui nama tampilan, username, atau alamat email akun Anda</div>',
                unsafe_allow_html=True,
            )
            with st.form("form_update_profile"):
                st.text_input("Peran Akses (Role)", value=user.display_role, disabled=True)
                new_nama = st.text_input("Nama Lengkap / Jabatan", value=user.nama)
                new_username = st.text_input("Username", value=user.username)
                new_email = st.text_input("Alamat Email", value=user.email)
                save_prof = st.form_submit_button("Simpan Perubahan Profil", type="primary", use_container_width=True)

            if save_prof:
                err = update_current_profile(new_username, new_nama, new_email)
                if err:
                    st.error(err)
                else:
                    st.success("Profil dan username berhasil diperbarui.")
                    st.rerun()

    # Kartu 2: Ganti Kata Sandi
    with col_right:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Ubah Kata Sandi</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="chart-subtitle">Gunakan kombinasi minimal 6 karakter demi keamanan data madrasah</div>',
                unsafe_allow_html=True,
            )
            with st.form("form_change_pw"):
                old_pw = st.text_input("Kata Sandi Saat Ini", type="password")
                new_pw = st.text_input("Kata Sandi Baru", type="password")
                conf_pw = st.text_input("Ulangi Kata Sandi Baru", type="password")
                save_pw = st.form_submit_button("Perbarui Kata Sandi", type="primary", use_container_width=True)

            if save_pw:
                if not old_pw or not new_pw:
                    st.error("Seluruh kolom kata sandi wajib diisi.")
                elif new_pw != conf_pw:
                    st.error("Konfirmasi kata sandi baru tidak cocok.")
                else:
                    err = change_current_password(old_pw, new_pw)
                    if err:
                        st.error(err)
                    else:
                        st.success("Kata sandi berhasil diperbarui.")

    # Kartu 3 (Khusus Operator / Super Admin): Manajemen Reset Password Pengguna Lain
    if user.is_operator:
        st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(
                '<div class="chart-title">Panel Super Admin — Manajemen Akun Pengguna</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="chart-subtitle">Khusus Operator (Super Admin): pantau daftar peran pengguna dan bantu reset kata sandi jika Kepala Sekolah lupa password</div>',
                unsafe_allow_html=True,
            )
            if use_supabase():
                client = st.session_state.get("sb_client")
                try:
                    rows = client.table("profiles").select("id,nama,role").execute().data
                    if rows:
                        for r in rows:
                            r["role"] = role_label(r["role"])
                        st.dataframe(rows, hide_index=True, use_container_width=True)
                except Exception:
                    st.info("Daftar profil dapat dikelola langsung melalui menu Authentication > Users di dasbor Supabase.")
                st.caption("Untuk reset kata sandi pengguna pada mode Supabase, pengguna dapat memakai tab 'Lupa Kata Sandi' di halaman login atau melalui Supabase Auth.")
            else:
                store = LocalAccountStore()
                users_list = store.list_users()
                display_users = [
                    {
                        "Username": u["username"],
                        "Nama": u["nama"],
                        "Email": u["email"],
                        "Hak Akses": role_label(u["role"]),
                    }
                    for u in users_list
                ]
                st.dataframe(display_users, hide_index=True, use_container_width=True)

                with st.form("admin_reset_form"):
                    c1, c2 = st.columns(2)
                    target_map = {f"{u['nama']} ({u['username']})": u["id"] for u in users_list}
                    selected_label = c1.selectbox("Pilih Akun yang Akan Direset", list(target_map.keys()))
                    admin_new_pw = c2.text_input("Kata Sandi Baru untuk Akun Terpilih", type="password")
                    btn_admin_reset = st.form_submit_button("Reset Kata Sandi Pengguna", type="primary")
                if btn_admin_reset:
                    err = store.admin_reset_password(target_map[selected_label], admin_new_pw)
                    if err:
                        st.error(err)
                    else:
                        st.success(f"Kata sandi untuk **{selected_label}** berhasil diatur ulang.")


render()
