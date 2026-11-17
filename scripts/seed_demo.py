"""Isi basis data lokal (SQLite) dengan data contoh:  python -m scripts.seed_demo"""
import numpy as np
import pandas as pd

from data.repository import LocalRepo

rng = np.random.default_rng(7)
rows = []
for i, y in enumerate(range(2018, 2026)):
    for kelas, base in (("VII", 110), ("VIII", 104), ("IX", 98)):
        tot = int(base + i * 4 + rng.integers(-4, 5))
        l = int(tot * rng.uniform(0.46, 0.54))
        rows.append({"tahun_ajaran": f"{y}/{y + 1}", "kelas": kelas, "laki_laki": l, "perempuan": tot - l})
print(LocalRepo().upsert(pd.DataFrame(rows)), "baris contoh tersimpan")
