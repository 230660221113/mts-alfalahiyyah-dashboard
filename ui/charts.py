"""Grafik Altair (sudah bawaan Streamlit, tanpa dependensi tambahan)."""
from __future__ import annotations

import altair as alt
import pandas as pd

ACTUAL, FORECAST = "#1F4E79", "#E07B00"
_ORDER = ["VII", "VIII", "IX"]


def trend_line(totals: pd.DataFrame) -> alt.Chart:
    return (alt.Chart(totals).mark_line(point=True, color=ACTUAL).encode(
        x=alt.X("tahun_ajaran:N", title="Tahun ajaran", sort=None),
        y=alt.Y("total:Q", title="Jumlah siswa", scale=alt.Scale(zero=False)),
        tooltip=["tahun_ajaran", "total", "laki_laki", "perempuan"],
    ).properties(height=320))


def class_bars(per_class: pd.DataFrame) -> alt.Chart:
    return (alt.Chart(per_class).mark_bar().encode(
        x=alt.X("tahun_ajaran:N", title="Tahun ajaran", sort=None),
        y=alt.Y("total:Q", title="Jumlah siswa"),
        color=alt.Color("kelas:N", title="Kelas", sort=_ORDER,
                        scale=alt.Scale(domain=_ORDER, range=["#9DB9D5", "#4F81B3", ACTUAL])),
        tooltip=["tahun_ajaran", "kelas", "total"],
    ).properties(height=320))


def gender_bars(totals: pd.DataFrame) -> alt.Chart:
    long = totals.melt(id_vars="tahun_ajaran", value_vars=["laki_laki", "perempuan"],
                       var_name="jenis", value_name="jumlah")
    return (alt.Chart(long).mark_bar().encode(
        x=alt.X("tahun_ajaran:N", title="Tahun ajaran", sort=None),
        y=alt.Y("jumlah:Q", title="Jumlah siswa"),
        color=alt.Color("jenis:N", title="Jenis kelamin",
                        scale=alt.Scale(domain=["laki_laki", "perempuan"], range=[ACTUAL, "#7FB3A5"])),
        xOffset="jenis:N",
        tooltip=["tahun_ajaran", "jenis", "jumlah"],
    ).properties(height=320))


def forecast_chart(history: pd.DataFrame, fc: pd.DataFrame) -> alt.Chart:
    """history: tahun_ajaran,total ; fc: tahun_ajaran,total (prediksi)."""
    hist = history[["tahun_ajaran", "total"]].assign(jenis="Aktual")
    bridge = hist.tail(1).assign(jenis="Prediksi")  # sambungkan garis aktual -> prediksi
    pred = fc[["tahun_ajaran", "total"]].assign(jenis="Prediksi")
    data = pd.concat([hist, bridge, pred], ignore_index=True)
    return (alt.Chart(data).mark_line(point=True).encode(
        x=alt.X("tahun_ajaran:N", title="Tahun ajaran", sort=None),
        y=alt.Y("total:Q", title="Jumlah siswa", scale=alt.Scale(zero=False)),
        color=alt.Color("jenis:N", title="", scale=alt.Scale(domain=["Aktual", "Prediksi"],
                                                                range=[ACTUAL, FORECAST])),
        strokeDash=alt.StrokeDash("jenis:N", legend=None,
                                  scale=alt.Scale(domain=["Aktual", "Prediksi"], range=[[1, 0], [6, 4]])),
        tooltip=["tahun_ajaran", "total", "jenis"],
    ).properties(height=360))
