import streamlit as st

# Akun demo. Ganti dengan Supabase Auth (sign_in_with_password) + RLS.
DEMO = {"operator": {"password": "operator123", "role": "Operator"},
        "pimpinan": {"password": "pimpinan123", "role": "Pimpinan"}}

def require_login() -> str:
    if "role" in st.session_state:
        return st.session_state["role"]
    users = st.secrets.get("users", DEMO)
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        st.markdown("<div class='page-title' style='margin-top:12vh'>Masuk</div><div class='page-sub'>Dashboard Kesiswaan MTs Al-Falahiyyah</div>", unsafe_allow_html=True)
        u = st.text_input("Nama pengguna")
        p = st.text_input("Kata sandi", type="password")
        if st.button("Masuk"):
            acc = users.get(u)
            if acc and acc["password"] == p:
                st.session_state["role"] = acc["role"]
                st.rerun()
            st.error("Nama pengguna atau kata sandi salah.")
    st.stop()

def logout():
    st.session_state.clear()
    st.rerun()
