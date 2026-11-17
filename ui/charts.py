"""Grafik Altair modern dengan palet harmonis, label nilai, dan tooltip kaya."""
from __future__ import annotations

import altair as alt
import pandas as pd

PRIMARY = "#0F4C81"
SECONDARY = "#1687A7"
ACCENT = "#E07B00"
TEAL = "#10B981"
SLATE = "#64748B"
_ORDER = ["VII", "VIII", "IX"]


def _base_config(chart: alt.Chart) -> alt.Chart:
    return (
        chart.configure_axis(
            labelFont="Plus Jakarta Sans, sans-serif",
            titleFont="Plus Jakarta Sans, sans-serif",
            labelFontSize=11,
            titleFontSize=12,
            labelColor="#475569",
            titleColor="#334155",
            gridColor="#EEF2F6",
            domainColor="#CBD5E1",
            tickColor="#CBD5E1",
        )
        .configure_legend(
            labelFont="Plus Jakarta Sans, sans-serif",
            titleFont="Plus Jakarta Sans, sans-serif",
            labelFontSize=11,
            titleFontSize=11,
            orient="top",
            padding=6,
        )
        .configure_view(strokeWidth=0)
    )


def trend_line(totals: pd.DataFrame) -> alt.Chart:
    """Grafik area + garis tren total siswa dengan titik dan label angka."""
    base = alt.Chart(totals).encode(
        x=alt.X("tahun_ajaran:N", title="Tahun Ajaran", sort=None, axis=alt.Axis(labelAngle=-30)),
        y=alt.Y("total:Q", title="Jumlah Siswa", scale=alt.Scale(zero=False, padding=15)),
        tooltip=[
            alt.Tooltip("tahun_ajaran:N", title="Tahun Ajaran"),
            alt.Tooltip("total:Q", title="Total Siswa", format=","),
            alt.Tooltip("laki_laki:Q", title="Laki-laki", format=","),
            alt.Tooltip("perempuan:Q", title="Perempuan", format=","),
        ],
    )

    area = base.mark_area(
        line={"color": PRIMARY, "strokeWidth": 3},
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="rgba(15, 76, 129, 0.24)", offset=0),
                alt.GradientStop(color="rgba(15, 76, 129, 0.01)", offset=1),
            ],
            x1=1,
            x2=1,
            y1=1,
            y2=0,
        ),
    )

    points = base.mark_circle(size=75, color=PRIMARY, stroke="#FFFFFF", strokeWidth=2)

    labels = base.mark_text(
        align="center",
        baseline="bottom",
        dy=-10,
        fontSize=11,
        fontWeight="bold",
        color="#0F172A",
    ).encode(text=alt.Text("total:Q", format=","))

    return _base_config((area + points + labels).properties(height=320))


def class_bars(per_class: pd.DataFrame) -> alt.Chart:
    """Grafik batang bertumpuk komposisi siswa per tingkat kelas (VII, VIII, IX)."""
    chart = (
        alt.Chart(per_class)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=28)
        .encode(
            x=alt.X("tahun_ajaran:N", title="Tahun Ajaran", sort=None, axis=alt.Axis(labelAngle=-30)),
            y=alt.Y("total:Q", title="Jumlah Siswa"),
            color=alt.Color(
                "kelas:N",
                title="Tingkat Kelas",
                sort=_ORDER,
                scale=alt.Scale(domain=_ORDER, range=["#7DD3FC", "#0284C7", PRIMARY]),
            ),
            order=alt.Order("kelas:N", sort="ascending"),
            tooltip=[
                alt.Tooltip("tahun_ajaran:N", title="Tahun Ajaran"),
                alt.Tooltip("kelas:N", title="Kelas"),
                alt.Tooltip("laki_laki:Q", title="Laki-laki", format=","),
                alt.Tooltip("perempuan:Q", title="Perempuan", format=","),
                alt.Tooltip("total:Q", title="Total", format=","),
            ],
        )
        .properties(height=320)
    )
    return _base_config(chart)


def gender_bars(totals: pd.DataFrame) -> alt.Chart:
    """Grafik batang berkelompok perbandingan Laki-laki vs Perempuan."""
    long = totals.melt(
        id_vars="tahun_ajaran",
        value_vars=["laki_laki", "perempuan"],
        var_name="jenis_raw",
        value_name="jumlah",
    )
    label_map = {"laki_laki": "Laki-laki", "perempuan": "Perempuan"}
    long["jenis"] = long["jenis_raw"].map(label_map)

    base = alt.Chart(long).encode(
        x=alt.X("tahun_ajaran:N", title="Tahun Ajaran", sort=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("jumlah:Q", title="Jumlah Siswa", scale=alt.Scale(padding=12)),
        xOffset="jenis:N",
        color=alt.Color(
            "jenis:N",
            title="Jenis Kelamin",
            scale=alt.Scale(domain=["Laki-laki", "Perempuan"], range=[PRIMARY, TEAL]),
        ),
        tooltip=[
            alt.Tooltip("tahun_ajaran:N", title="Tahun Ajaran"),
            alt.Tooltip("jenis:N", title="Jenis Kelamin"),
            alt.Tooltip("jumlah:Q", title="Jumlah", format=","),
        ],
    )

    bars = base.mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, size=24)
    labels = base.mark_text(
        align="center",
        baseline="bottom",
        dy=-5,
        fontSize=10,
        fontWeight="bold",
        color="#334155",
    ).encode(text=alt.Text("jumlah:Q", format=","))

    return _base_config((bars + labels).properties(height=310))


def forecast_chart(history: pd.DataFrame, fc: pd.DataFrame) -> alt.Chart:
    """Grafik gabungan data aktual dan proyeksi masa depan dengan label nilai."""
    hist = history[["tahun_ajaran", "total"]].assign(jenis="Data Aktual")
    bridge = hist.tail(1).assign(jenis="Proyeksi Prediksi")
    pred = fc[["tahun_ajaran", "total"]].assign(jenis="Proyeksi Prediksi")
    data = pd.concat([hist, bridge, pred], ignore_index=True)

    # Data khusus label (tanpa titik bridge ganda)
    label_df = pd.concat([hist, pred], ignore_index=True)

    base = alt.Chart(data).encode(
        x=alt.X("tahun_ajaran:N", title="Tahun Ajaran", sort=None, axis=alt.Axis(labelAngle=-25)),
        y=alt.Y("total:Q", title="Jumlah Peserta Didik", scale=alt.Scale(zero=False, padding=18)),
        color=alt.Color(
            "jenis:N",
            title="Keterangan",
            scale=alt.Scale(domain=["Data Aktual", "Proyeksi Prediksi"], range=[PRIMARY, ACCENT]),
        ),
        tooltip=[
            alt.Tooltip("tahun_ajaran:N", title="Tahun Ajaran"),
            alt.Tooltip("total:Q", title="Jumlah Siswa", format=","),
            alt.Tooltip("jenis:N", title="Status"),
        ],
    )

    lines = base.mark_line(strokeWidth=3).encode(
        strokeDash=alt.StrokeDash(
            "jenis:N",
            legend=None,
            scale=alt.Scale(domain=["Data Aktual", "Proyeksi Prediksi"], range=[[1, 0], [7, 5]]),
        )
    )

    points = base.mark_circle(size=85, stroke="#FFFFFF", strokeWidth=2)

    labels = (
        alt.Chart(label_df)
        .mark_text(
            align="center",
            baseline="bottom",
            dy=-11,
            fontSize=11,
            fontWeight="bold",
        )
        .encode(
            x=alt.X("tahun_ajaran:N", sort=None),
            y=alt.Y("total:Q"),
            text=alt.Text("total:Q", format=","),
            color=alt.Color(
                "jenis:N",
                legend=None,
                scale=alt.Scale(domain=["Data Aktual", "Proyeksi Prediksi"], range=[PRIMARY, ACCENT]),
            ),
        )
    )

    return _base_config((lines + points + labels).properties(height=360))
