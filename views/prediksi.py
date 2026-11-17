import math
import pandas as pd
import streamlit as st

from core.config import MAX_HORIZON, MIN_POINTS, school_name
from data.repository import get_repo
from data.transform import yearly_totals, year_label
from forecasting.evaluation import best_model, compare_models, forecast
from forecasting.models import HAS_STATSMODELS, available_models
from ui import charts
from ui.styles import render_hero, render_kpi_card


@st.cache_data(show_spinner="Mengevaluasi keempat algoritma peramalan...")
def _compare(y: tuple) -> pd.DataFrame:
    return compare_models(list(y))


def render() -> None:
    df = get_repo().fetch_all()
    tot = yearly_totals(df)

    render_hero(
        title="Prediksi Jumlah Peserta Didik",
        subtitle=f"Peramalan kebutuhan rombongan belajar & daya tampung {school_name()} berbasis evaluasi multi-algoritma.",
        badge_text=f"🤖 Basis Data: {len(tot)} Tahun Ajaran",
    )

    if len(tot) < MIN_POINTS:
        st.warning(
            f"Prediksi membutuhkan minimal **{MIN_POINTS} tahun ajaran** data berurutan "
            f"(saat ini baru tersedia **{len(tot)} tahun ajaran**)."
        )
        return
    if not HAS_STATSMODELS:
        st.warning("Paket `statsmodels` belum terpasang: Holt’s Exponential Smoothing dan ARIMA dilewati.")

    y = tuple(int(v) for v in tot["total"])
    table = _compare(y)
    best = best_model(table)

    # Panel Kontrol Prediksi
    with st.container(border=True):
        c1, c2 = st.columns([1.1, 1])
        horizon = c1.slider("Horizon Proyeksi (Tahun Ajaran Mendatang)", 1, MAX_HORIZON, 3)
        choice = c2.selectbox("Algoritma Peramalan", ["Otomatis (Error Terkecil)"] + list(available_models()))
        model = best if choice.startswith("Otomatis") else choice

    pred = forecast(y, model, horizon)
    last = int(tot["mulai"].iloc[-1])
    fc = pd.DataFrame(
        {
            "tahun_ajaran": [year_label(last + i + 1) for i in range(horizon)],
            "total": pred.astype(int),
        }
    )

    # Sorotan Ringkasan Hasil Prediksi Tahun Berikutnya
    next_ta = fc.iloc[0]["tahun_ajaran"]
    next_val = int(fc.iloc[0]["total"])
    last_val = int(tot["total"].iloc[-1])
    diff_next = next_val - last_val
    est_rombel = math.ceil(next_val / 30)
    best_rmse = table.loc[table["model"] == model, "RMSE"].values[0] if "model" in table.columns else 0

    k1, k2, k3 = st.columns(3)
    with k1:
        render_kpi_card(
            label=f"Proyeksi TA {next_ta}",
            value=f"{next_val:,} Siswa",
            subtext=f"{'▲' if diff_next >= 0 else '▼'} {diff_next:+d} dari TA {tot.iloc[-1]['tahun_ajaran']}",
            badge_type="up" if diff_next >= 0 else "down",
            icon="🎯",
            icon_bg="#FFEDD5",
            icon_color="#C2410C",
        )
    with k2:
        render_kpi_card(
            label=f"Estimasi Kebutuhan Rombel ({next_ta})",
            value=f"{est_rombel} Rombel",
            subtext="Asumsi kapasitas ideal 30 siswa/kelas",
            badge_type="neutral",
            icon="🏫",
            icon_bg="#E0F2FE",
            icon_color="#0369A1",
        )
    with k3:
        render_kpi_card(
            label="Algoritma Aktif",
            value=model,
            subtext=f"RMSE Evaluasi: {best_rmse:.2f}" + (" · Terbaik" if model == best else ""),
            badge_type="up" if model == best else "neutral",
            icon="⚙️",
            icon_bg="#DCFCE7",
            icon_color="#15803D",
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Grafik Utama Proyeksi
    with st.container(border=True):
        st.markdown('<div class="chart-title">Grafik Aktual vs Proyeksi Peserta Didik</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="chart-subtitle">Garis biru menunjukkan data historis aktual, sedangkan garis putus-putus oranye menunjukkan hasil peramalan menggunakan <b>{model}</b></div>',
            unsafe_allow_html=True,
        )
        st.altair_chart(charts.forecast_chart(tot, fc), use_container_width=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Tabel Hasil Prediksi & Evaluasi Error
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Tabel Angka Proyeksi</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-subtitle">Estimasi total siswa beserta perkiraan rombongan belajar</div>', unsafe_allow_html=True)
            fc_display = fc.copy()
            fc_display["estimasi_rombel"] = fc_display["total"].apply(lambda x: f"{math.ceil(x / 30)} Rombel")
            fc_display = fc_display.rename(
                columns={
                    "tahun_ajaran": "Tahun Ajaran",
                    "total": "Prediksi Siswa",
                    "estimasi_rombel": "Estimasi Rombel",
                }
            )
            st.dataframe(fc_display, hide_index=True, use_container_width=True)
            st.download_button(
                "Unduh Hasil Prediksi (.csv)",
                fc.to_csv(index=False).encode(),
                "prediksi_siswa_mts_alfalahiyyah.csv",
                "text/csv",
                icon=":material/download:",
            )

    with right:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Komparasi Akurasi Algoritma</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-subtitle">Evaluasi backtest satu langkah ke depan (semakin kecil semakin akurat)</div>', unsafe_allow_html=True)
            st.dataframe(table.round(2), hide_index=True, use_container_width=True)
            st.caption("Metrik evaluasi: MAE (Mean Absolute Error), RMSE (Root Mean Squared Error), MAPE (%).")


render()
