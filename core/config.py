"""Konfigurasi aplikasi. Semua nilai rahasia dibaca dari .streamlit/secrets.toml."""
from __future__ import annotations

import streamlit as st

APP_TITLE = "Dashboard Analitik Kesiswaan"
from core.constants import (  # noqa: F401
    KELAS_VALID, MAX_HORIZON, MIN_POINTS, ROLE_OPERATOR, ROLE_PIMPINAN,
)


def secret(key: str, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return default


def school_name() -> str:
    return secret("SCHOOL_NAME", "MTs Al-Falahiyyah")


def use_supabase() -> bool:
    """True jika kredensial Supabase tersedia; jika tidak, mode demo lokal (SQLite)."""
    return bool(secret("SUPABASE_URL") and secret("SUPABASE_KEY"))
