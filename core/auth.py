"""Autentikasi & peran. Supabase Auth untuk produksi, akun demo untuk mode lokal."""
from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from core.config import ROLE_OPERATOR, ROLE_PIMPINAN, secret, use_supabase


@dataclass(frozen=True)
class User:
    email: str
    nama: str
    role: str

    @property
    def is_operator(self) -> bool:
        return self.role == ROLE_OPERATOR


def current_user() -> User | None:
    return st.session_state.get("user")


def _demo_accounts() -> dict[str, User]:
    return {
        "operator": User("operator", "Operator Demo", ROLE_OPERATOR),
        "pimpinan": User("pimpinan", "Kepala Madrasah (Demo)", ROLE_PIMPINAN),
    }


def login(identity: str, password: str) -> str | None:
    """Kembalikan pesan error, atau None bila berhasil."""
    if not identity or not password:
        return "Email dan kata sandi wajib diisi."

    if use_supabase():
        try:
            from supabase import create_client

            client = create_client(secret("SUPABASE_URL"), secret("SUPABASE_KEY"))
            res = client.auth.sign_in_with_password({"email": identity, "password": password})
            profile = (
                client.table("profiles").select("nama,role")
                .eq("id", res.user.id).single().execute().data
            )
        except Exception:
            return "Email atau kata sandi salah, atau profil pengguna belum dibuat."
        st.session_state["sb_client"] = client
        st.session_state["user"] = User(identity, profile.get("nama") or identity, profile["role"])
        return None

    demo_pw = secret("DEMO_PASSWORD", "demo123")
    user = _demo_accounts().get(identity.strip().lower())
    if user and password == demo_pw:
        st.session_state["user"] = user
        return None
    return "Akun demo tidak dikenal atau kata sandi salah."


def logout() -> None:
    client = st.session_state.get("sb_client")
    if client is not None:
        try:
            client.auth.sign_out()
        except Exception:
            pass
    st.session_state.clear()
    st.rerun()
