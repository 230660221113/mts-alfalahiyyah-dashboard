import streamlit as st
from src import visualization as viz

# Akun demo. Ganti dengan Supabase Auth (sign_in_with_password) + RLS.
DEMO = {
    "operator": {"password": "operator123", "role": "Operator"},
    "pimpinan": {"password": "pimpinan123", "role": "Pimpinan"},
}

HERO = f"""
<div class='login-visual'>
  <div class='login-brand'><span class='brand-mark'>✦</span><div><b>MTs Al-Falahiyyah</b><small>PORTAL DATA KESISWAAN</small></div></div>
  <div class='visual-content'>
    <div class='visual-kicker'><span></span> EDUCATION ANALYTICS</div>
    <h2>Data yang tertata.<br><em>Keputusan lebih terarah.</em></h2>
    <p>Pantau perkembangan peserta didik, pahami tren, dan siapkan perencanaan sekolah melalui satu ruang informasi.</p>
    <div class='visual-preview'>
      <div class='preview-head'><span>Perkembangan peserta didik</span><span class='preview-live'>● DATA</span></div>
      <div class='preview-number'>Tren kesiswaan <small>8 tahun ajaran</small></div>
      <div class='preview-bars'><i style='height:34%'></i><i style='height:43%'></i><i style='height:49%'></i><i style='height:57%'></i><i style='height:63%'></i><i style='height:72%'></i><i style='height:82%'></i><i style='height:91%'></i></div>
      <div class='preview-years'><span>2019</span><span>2021</span><span>2023</span><span>2026</span></div>
    </div>
  </div>
  <div class='visual-foot'><span>INFORMASI KESISWAAN TERINTEGRASI</span><span>© MTs Al-Falahiyyah</span></div>
</div>
"""


def require_login() -> str:
    if "role" in st.session_state:
        return st.session_state["role"]

    custom = "users" in st.secrets
    users = st.secrets["users"] if custom else DEMO

    st.markdown("<div class='login-page-label'>SISTEM INFORMASI KESISWAAN</div>", unsafe_allow_html=True)
    left, right = st.columns([0.88, 1.12], gap="large")
    with left:
        with st.container(key="login-panel"):
            st.markdown(
                "<div class='login-welcome'><span class='login-eyebrow'>SELAMAT DATANG KEMBALI</span>"
                "<h1>Masuk ke<br>dashboard Anda.</h1>"
                "<p>Gunakan akun yang telah diberikan untuk mengakses informasi kesiswaan sekolah.</p></div>",
                unsafe_allow_html=True,
            )
            with st.form("login", clear_on_submit=False):
                u = st.text_input("Nama pengguna", placeholder="Contoh: operator")
                p = st.text_input("Kata sandi", type="password", placeholder="Masukkan kata sandi")
                ok = st.form_submit_button("Masuk ke dashboard  →", use_container_width=True)
            if ok:
                acc = users.get(u.strip().lower())
                if acc and acc["password"] == p:
                    st.session_state["role"] = acc["role"]
                    st.rerun()
                st.error("Nama pengguna atau kata sandi tidak sesuai.")
            if not custom:
                st.markdown(
                    "<div class='demo-hint'><b>Akses demo</b><span>Operator: <code>operator</code> / <code>operator123</code></span>"
                    "<span>Pimpinan: <code>pimpinan</code> / <code>pimpinan123</code></span></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("<div class='login-security'>Akses terbatas · Pastikan akun Anda terjaga</div>", unsafe_allow_html=True)
    with right:
        st.markdown(HERO, unsafe_allow_html=True)
    st.stop()


def logout():
    st.session_state.clear()
    st.rerun()
