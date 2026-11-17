import streamlit as st
from src import visualization as viz

# Akun demo. Ganti dengan Supabase Auth (sign_in_with_password) + RLS.
DEMO = {"operator": {"password": "operator123", "role": "Operator"},
        "pimpinan": {"password": "pimpinan123", "role": "Pimpinan"}}

HERO = f"""
<div class='hero'>
  <div style='font-weight:800'>🎓 MTs Al-Falahiyyah</div>
  <div>
    <div class='mini'><div class='l'>Peserta didik</div><div class='n'>Tren per tahun ajaran</div>{viz.sparkline([3, 4, 4, 6, 7, 9, 8, 11], "#2F5D50")}</div>
    <div class='mini b'><div class='l'>Prediksi</div><div class='n'>Tahun ajaran berikutnya</div>{viz.sparkline([3, 4, 5, 5, 7, 8, 10, 12], "#A5D17A")}</div>
  </div>
  <div>
    <h2>Pantau dan prediksi jumlah peserta didik dalam satu dashboard</h2>
    <p>Unggah data, lihat perkembangannya, dan rencanakan kelas tahun depan.</p>
    <p class='note' style='margin-top:14px'>Gambar di atas hanya contoh tampilan.</p>
  </div>
</div>
"""

def require_login() -> str:
    if "role" in st.session_state:
        return st.session_state["role"]
    custom = "users" in st.secrets
    users = st.secrets["users"] if custom else DEMO
    left, right = st.columns([1, 1.1], gap="large")
    with left:
        st.markdown("<div style='height:14vh'></div><div class='login-title'>Selamat datang</div>"
                    "<div class='login-sub'>Masuk untuk melihat dashboard kesiswaan.</div>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Nama pengguna", placeholder="Masukkan nama pengguna")
            p = st.text_input("Kata sandi", type="password", placeholder="Masukkan kata sandi")
            ok = st.form_submit_button("Masuk", use_container_width=True)
        if ok:
            acc = users.get(u)
            if acc and acc["password"] == p:
                st.session_state["role"] = acc["role"]
                st.rerun()
            st.error("Nama pengguna atau kata sandi salah.")
        if not custom:
            st.markdown("<div class='demo-hint'><b>Akun demo</b><br>Operator: operator / operator123<br>Pimpinan: pimpinan / pimpinan123</div>", unsafe_allow_html=True)
    with right:
        st.markdown(HERO, unsafe_allow_html=True)
    st.stop()

def logout():
    st.session_state.clear()
    st.rerun()
