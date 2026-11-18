"""Autentikasi, manajemen peran, pengaturan akun, dan pemulihan kata sandi."""
from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

from core.config import (
    KEPALA_ROLES,
    ROLE_KEPALA_SEKOLAH,
    ROLE_OPERATOR,
    role_label,
    secret,
    use_supabase,
)


@dataclass(frozen=True)
class User:
    id: str
    email: str
    username: str
    nama: str
    role: str

    @property
    def is_operator(self) -> bool:
        return self.role == ROLE_OPERATOR

    @property
    def is_kepala_sekolah(self) -> bool:
        return self.role in KEPALA_ROLES

    @property
    def display_role(self) -> str:
        return role_label(self.role)


def _hash_pw(pw: str) -> str:
    return hashlib.sha256(f"mts_alfalahiyyah_salt::{pw}".encode("utf-8")).hexdigest()


class LocalAccountStore:
    """Penyimpanan akun lokal (SQLite) saat Supabase tidak dikonfigurasi."""

    def __init__(self, path: str | Path = "local_demo.db"):
        self.path = str(path)
        with self._conn() as c:
            c.execute(
                """CREATE TABLE IF NOT EXISTS users_local (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    nama TEXT NOT NULL,
                    role TEXT NOT NULL,
                    password_hash TEXT NOT NULL
                )"""
            )
            cur = c.execute("SELECT COUNT(*) FROM users_local")
            if cur.fetchone()[0] == 0:
                default_pw = secret("DEMO_PASSWORD", "demo123")
                seeds = [
                    (
                        "op-001",
                        "operator",
                        "operator@alfalahiyyah.sch.id",
                        "Operator Madrasah",
                        ROLE_OPERATOR,
                        _hash_pw(default_pw),
                    ),
                    (
                        "ks-001",
                        "kepsek",
                        "kepsek@alfalahiyyah.sch.id",
                        "Kepala MTs Al-Falahiyyah",
                        ROLE_KEPALA_SEKOLAH,
                        _hash_pw(default_pw),
                    ),
                ]
                c.executemany(
                    "INSERT INTO users_local (id, username, email, nama, role, password_hash) VALUES (?,?,?,?,?,?)",
                    seeds,
                )

    def _conn(self):
        return sqlite3.connect(self.path)

    def authenticate(self, identity: str, password: str) -> User | None:
        ident = identity.strip().lower()
        pw_h = _hash_pw(password)
        with self._conn() as c:
            row = c.execute(
                """SELECT id, email, username, nama, role FROM users_local
                   WHERE (LOWER(username)=? OR LOWER(email)=?) AND password_hash=?""",
                (ident, ident, pw_h),
            ).fetchone()
        if not row:
            return None
        return User(id=row[0], email=row[1], username=row[2], nama=row[3], role=row[4])

    def list_users(self) -> list[dict]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT id, username, email, nama, role FROM users_local ORDER BY role DESC, username ASC"
            ).fetchall()
        return [
            {"id": r[0], "username": r[1], "email": r[2], "nama": r[3], "role": r[4]}
            for r in rows
        ]

    def update_profile(self, user_id: str, new_username: str, new_nama: str, new_email: str) -> str | None:
        u_clean = new_username.strip().lower()
        e_clean = new_email.strip().lower()
        n_clean = new_nama.strip()
        if not u_clean or not n_clean or not e_clean:
            return "Nama lengkap, username, dan email tidak boleh kosong."
        if " " in u_clean:
            return "Username tidak boleh mengandung spasi."
        try:
            with self._conn() as c:
                c.execute(
                    "UPDATE users_local SET username=?, nama=?, email=? WHERE id=?",
                    (u_clean, n_clean, e_clean, user_id),
                )
        except sqlite3.IntegrityError:
            return "Username atau email sudah digunakan akun lain."
        return None

    def change_password(self, user_id: str, old_pw: str, new_pw: str) -> str | None:
        if len(new_pw) < 6:
            return "Kata sandi baru minimal 6 karakter."
        with self._conn() as c:
            row = c.execute("SELECT password_hash FROM users_local WHERE id=?", (user_id,)).fetchone()
            if not row or row[0] != _hash_pw(old_pw):
                return "Kata sandi lama tidak sesuai."
            c.execute("UPDATE users_local SET password_hash=? WHERE id=?", (_hash_pw(new_pw), user_id))
        return None

    def reset_password_by_identity(self, identity: str, new_pw: str) -> str | None:
        if len(new_pw) < 6:
            return "Kata sandi baru minimal 6 karakter."
        ident = identity.strip().lower()
        with self._conn() as c:
            row = c.execute(
                "SELECT id FROM users_local WHERE LOWER(username)=? OR LOWER(email)=?",
                (ident, ident),
            ).fetchone()
            if not row:
                return "Akun dengan username atau email tersebut tidak ditemukan."
            c.execute("UPDATE users_local SET password_hash=? WHERE id=?", (_hash_pw(new_pw), row[0]))
        return None

    def admin_reset_password(self, target_user_id: str, new_pw: str) -> str | None:
        if len(new_pw) < 6:
            return "Kata sandi baru minimal 6 karakter."
        with self._conn() as c:
            c.execute(
                "UPDATE users_local SET password_hash=? WHERE id=?",
                (_hash_pw(new_pw), target_user_id),
            )
        return None


def current_user() -> User | None:
    return st.session_state.get("user")


def login(identity: str, password: str) -> str | None:
    """Kembalikan pesan error, atau None bila berhasil."""
    if not identity or not password:
        return "Username/email dan kata sandi wajib diisi."

    if use_supabase():
        try:
            from supabase import create_client

            client = create_client(secret("SUPABASE_URL"), secret("SUPABASE_KEY"))
            res = client.auth.sign_in_with_password({"email": identity.strip(), "password": password})
            profile = (
                client.table("profiles")
                .select("nama,role,username")
                .eq("id", res.user.id)
                .single()
                .execute()
                .data
            )
        except Exception:
            # Fallback jika kolom username belum ditambahkan di schema lama
            try:
                from supabase import create_client

                client = create_client(secret("SUPABASE_URL"), secret("SUPABASE_KEY"))
                res = client.auth.sign_in_with_password({"email": identity.strip(), "password": password})
                profile = (
                    client.table("profiles")
                    .select("nama,role")
                    .eq("id", res.user.id)
                    .single()
                    .execute()
                    .data
                )
            except Exception:
                return "Email atau kata sandi salah, atau profil pengguna belum dibuat."

        st.session_state["sb_client"] = client
        uname = profile.get("username") or identity.split("@")[0]
        st.session_state["user"] = User(
            id=str(res.user.id),
            email=identity.strip(),
            username=uname,
            nama=profile.get("nama") or uname,
            role=profile["role"],
        )
        return None

    store = LocalAccountStore()
    user = store.authenticate(identity, password)
    if user:
        st.session_state["user"] = user
        return None
    return "Username/email tidak dikenal atau kata sandi salah."


def update_current_profile(new_username: str, new_nama: str, new_email: str) -> str | None:
    user = current_user()
    if not user:
        return "Sesi berakhir. Silakan login kembali."

    if use_supabase():
        client = st.session_state.get("sb_client")
        try:
            payload = {"nama": new_nama.strip()}
            if new_username.strip():
                payload["username"] = new_username.strip().lower()
            client.table("profiles").update(payload).eq("id", user.id).execute()
            if new_email.strip() and new_email.strip().lower() != user.email.lower():
                client.auth.update_user({"email": new_email.strip()})
            st.session_state["user"] = User(
                id=user.id,
                email=new_email.strip() or user.email,
                username=new_username.strip().lower() or user.username,
                nama=new_nama.strip() or user.nama,
                role=user.role,
            )
            return None
        except Exception as e:
            return f"Gagal memperbarui profil di Supabase: {e}"

    store = LocalAccountStore()
    err = store.update_profile(user.id, new_username, new_nama, new_email)
    if err:
        return err
    st.session_state["user"] = User(
        id=user.id,
        email=new_email.strip().lower(),
        username=new_username.strip().lower(),
        nama=new_nama.strip(),
        role=user.role,
    )
    return None


def change_current_password(old_pw: str, new_pw: str) -> str | None:
    user = current_user()
    if not user:
        return "Sesi berakhir. Silakan login kembali."
    if len(new_pw) < 6:
        return "Kata sandi baru minimal 6 karakter."

    if use_supabase():
        client = st.session_state.get("sb_client")
        try:
            # Verifikasi kata sandi lama terlebih dahulu
            client.auth.sign_in_with_password({"email": user.email, "password": old_pw})
            client.auth.update_user({"password": new_pw})
            return None
        except Exception:
            return "Kata sandi lama salah atau gagal memperbarui kata sandi."

    return LocalAccountStore().change_password(user.id, old_pw, new_pw)


def request_password_reset(identity: str, new_pw_local: str = "", recovery_code: str = "") -> tuple[bool, str]:
    """Pemulihan lupa kata sandi untuk mode Supabase (email reset) maupun lokal."""
    if not identity.strip():
        return False, "Masukkan email atau username akun Anda."

    if use_supabase():
        try:
            from supabase import create_client

            client = create_client(secret("SUPABASE_URL"), secret("SUPABASE_KEY"))
            client.auth.reset_password_for_email(identity.strip())
            return True, f"Tautan pemulihan kata sandi telah dikirim ke email **{identity.strip()}**. Silakan periksa kotak masuk/spam Anda."
        except Exception as e:
            return False, f"Gagal mengirim email reset kata sandi: {e}"

    expected_code = secret("RECOVERY_CODE", "ALFALAHIYYAH2026")
    if recovery_code.strip() != expected_code:
        return False, "Kode pemulihan madrasah tidak valid. Hubungi Operator (Super Admin) untuk mendapatkan kode atau reset langsung."
    err = LocalAccountStore().reset_password_by_identity(identity, new_pw_local)
    if err:
        return False, err
    return True, "Kata sandi berhasil diatur ulang. Silakan masuk menggunakan kata sandi baru."


def logout() -> None:
    client = st.session_state.get("sb_client")
    if client is not None:
        try:
            client.auth.sign_out()
        except Exception:
            pass
    st.session_state.clear()
    st.rerun()
