import pandas as pd
import streamlit as st

from core.config import MAX_HORIZON, MIN_POINTS
from data.repository import get_repo
from data.transform import yearly_totals, year_label
from forecasting.evaluation import best_model, compare_models, forecast
from forecasting.models import HAS_STATSMODELS, available_models
from ui import charts


@st.cache_data(show_spinner="Mengevaluasi model...")
def _compare(y: tuple) -> pd.DataFrame:
    return compare_models(list(y))


def render() -> None:
    st.header("Prediksi Jumlah Peserta Didik")
    df = get_repo().fetch_all()
    tot = yearly_totals(df)

    if len(tot) < MIN_POINTS:
        st.warning(f"Prediksi membutuhkan minimal {MIN_POINTS} tahun ajaran data "
                   f"(saat ini {len(tot)}).")
        return
    if not HAS_STATSMODELS:
        st.warning("Paket `statsmodels` belum terpasang: Holt dan ARIMA dilewati.")

    y = tuple(int(v) for v in tot["total"])
    table = _compare(y)
    best = best_model(table)

    c1, c2 = st.columns(2)
    horizon = c1.slider("Horizon (tahun ajaran)", 1, MAX_HORIZON, 3)
    choice = c2.selectbox("Model", ["Otomatis (error terkecil)"] + list(available_models()))
    model = best if choice.startswith("Otomatis") else choice

    pred = forecast(y, model, horizon)
    last = int(tot["mulai"].iloc[-1])
    fc = pd.DataFrame({"tahun_ajaran": [year_label(last + i + 1) for i in range(horizon)],
                       "total": pred.astype(int)})

    st.caption(f"Model dipakai: **{model}**" + (" (terbaik berdasarkan RMSE)" if model == best else ""))
    st.altair_chart(charts.forecast_chart(tot, fc), use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Hasil prediksi")
        st.dataframe(fc.rename(columns={"total": "prediksi_siswa"}), hide_index=True,
                     use_container_width=True)
        st.download_button("Unduh CSV", fc.to_csv(index=False).encode(), "prediksi_siswa.csv",
                           "text/csv")
    with right:
        st.subheader("Perbandingan model")
        st.dataframe(table.round(2), hide_index=True, use_container_width=True)
        st.caption("Backtest satu langkah ke depan (expanding window). Semakin kecil semakin baik.")


render()
