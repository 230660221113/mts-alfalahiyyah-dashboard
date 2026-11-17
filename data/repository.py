"""Lapisan penyimpanan. UI hanya bicara ke `get_repo()`, tidak peduli backend-nya.

- SupabaseRepo : produksi (PostgreSQL + RLS, memakai sesi login pengguna).
- LocalRepo    : mode demo/pengembangan (SQLite), tanpa kredensial apa pun.
"""
from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd
import streamlit as st

from core.config import use_supabase
from data.transform import COLUMNS, empty_frame


class Repo(ABC):
    @abstractmethod
    def fetch_all(self) -> pd.DataFrame: ...

    @abstractmethod
    def upsert(self, df: pd.DataFrame) -> int:
        """Simpan/perbarui baris berdasarkan (tahun_ajaran, kelas). Kembalikan jumlah baris."""

    @abstractmethod
    def delete_year(self, tahun_ajaran: str) -> None: ...


class SupabaseRepo(Repo):
    TABLE = "siswa_rekap"

    def __init__(self, client):
        self.client = client

    def fetch_all(self) -> pd.DataFrame:
        rows = (self.client.table(self.TABLE).select(",".join(COLUMNS))
                .order("tahun_ajaran").execute().data)
        return pd.DataFrame(rows, columns=COLUMNS) if rows else empty_frame()

    def upsert(self, df: pd.DataFrame) -> int:
        records = df[COLUMNS].to_dict("records")
        self.client.table(self.TABLE).upsert(records, on_conflict="tahun_ajaran,kelas").execute()
        return len(records)

    def delete_year(self, tahun_ajaran: str) -> None:
        self.client.table(self.TABLE).delete().eq("tahun_ajaran", tahun_ajaran).execute()


class LocalRepo(Repo):
    def __init__(self, path: str | Path = "local_demo.db"):
        self.path = str(path)
        with self._conn() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS siswa_rekap (
                tahun_ajaran TEXT NOT NULL, kelas TEXT NOT NULL,
                laki_laki INTEGER NOT NULL, perempuan INTEGER NOT NULL,
                PRIMARY KEY (tahun_ajaran, kelas))""")

    def _conn(self):
        return sqlite3.connect(self.path)

    def fetch_all(self) -> pd.DataFrame:
        with self._conn() as c:
            df = pd.read_sql_query(f"SELECT {','.join(COLUMNS)} FROM siswa_rekap ORDER BY tahun_ajaran", c)
        return df if not df.empty else empty_frame()

    def upsert(self, df: pd.DataFrame) -> int:
        rows = [tuple(r) for r in df[COLUMNS].itertuples(index=False)]
        with self._conn() as c:
            c.executemany("""INSERT INTO siswa_rekap VALUES (?,?,?,?)
                ON CONFLICT(tahun_ajaran,kelas) DO UPDATE SET
                laki_laki=excluded.laki_laki, perempuan=excluded.perempuan""", rows)
        return len(rows)

    def delete_year(self, tahun_ajaran: str) -> None:
        with self._conn() as c:
            c.execute("DELETE FROM siswa_rekap WHERE tahun_ajaran=?", (tahun_ajaran,))


def get_repo() -> Repo:
    if use_supabase():
        return SupabaseRepo(st.session_state["sb_client"])
    return LocalRepo()
