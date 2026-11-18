import math

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def _lr(y, h):
    m = LinearRegression().fit(np.arange(len(y)).reshape(-1, 1), y)
    return m.predict(np.arange(len(y), len(y) + h).reshape(-1, 1))


def _holt(y, h):
    return ExponentialSmoothing(y, trend="add", damped_trend=True, initialization_method="estimated").fit().forecast(h)


def _arima(y, h):
    try:
        return ARIMA(y, order=(1, 1, 0), trend="t").fit().forecast(h)  # dengan drift
    except Exception:
        return ARIMA(y, order=(1, 1, 0)).fit().forecast(h)


def _rf(y, h):
    """Random Forest pada SELISIH antar-tahun, supaya bisa melampaui rentang data."""
    d = np.diff(y)
    m = RandomForestRegressor(n_estimators=200, random_state=42).fit(d[:-1].reshape(-1, 1), d[1:])
    last, ld, out = float(y[-1]), float(d[-1]), []
    for _ in range(h):
        ld = float(m.predict([[ld]])[0])
        last += ld
        out.append(last)
    return np.array(out)


MODELS = {"Regresi Linier": _lr, "Holt Exponential Smoothing": _holt, "ARIMA": _arima, "Random Forest": _rf}


def backtest(y: np.ndarray) -> pd.DataFrame:
    """Uji satu langkah ke depan pada beberapa tahun terakhir (expanding window).
    Galat dihitung pada data yang TIDAK dipakai melatih, bukan pada data latih."""
    n = len(y)
    k = min(3, n - 4)
    rows = []
    for name, fn in MODELS.items():
        try:
            e = np.array([y[t] - float(fn(y[:t], 1)[0]) for t in range(n - k, n)])
        except Exception:
            continue
        a = y[n - k:]
        rows.append({"Algoritma": name, "MAE": round(float(np.mean(abs(e))), 2),
                     "RMSE": round(float(np.sqrt(np.mean(e**2))), 2),
                     "MAPE": round(float(np.mean(abs(e / a)) * 100), 2)})
    return pd.DataFrame(rows).sort_values(["RMSE", "MAPE"]).reset_index(drop=True)


def run_auto_forecast(df_hist: pd.DataFrame, horizon: int = 2, kapasitas_rombel: int = 32, rasio_guru: int = 20) -> dict:
    """Menjalankan empat model di belakang layar, memilih yang galat ujinya terkecil,
    lalu menyusun proyeksi + kebutuhan rombel dan guru. Minimal 6 tahun ajaran."""
    df = df_hist.sort_values("tahun_mulai").reset_index(drop=True)
    y = df["total_aktif"].astype(float).values
    ev = backtest(y)
    best = ev.iloc[0]["Algoritma"] if not ev.empty else "Regresi Linier"
    pred = np.maximum(np.round(np.asarray(MODELS[best](y, horizon))), 0).astype(int)

    last_start, prev = int(df["tahun_mulai"].iloc[-1]), int(df["total_aktif"].iloc[-1])
    tot = df["total_aktif"].replace(0, np.nan)
    p_vii, p_viii = float((df["kelas_vii"] / tot).mean()), float((df["kelas_viii"] / tot).mean())
    if np.isnan(p_vii) or np.isnan(p_viii):
        p_vii, p_viii = 0.35, 0.33

    rows = []
    for i, total in enumerate(pred, start=1):
        total = int(total)
        vii, viii = int(round(total * p_vii)), int(round(total * p_viii))
        rows.append({"Tahun_Ajaran": f"{last_start + i}/{last_start + i + 1}", "Proyeksi_Siswa_Aktif": total,
                     "Est_Kelas_VII": vii, "Est_Kelas_VIII": viii, "Est_Kelas_IX": max(total - vii - viii, 0),
                     "Selisih": total - prev, "Kebutuhan_Rombel": max(math.ceil(total / kapasitas_rombel), 3),
                     "Kebutuhan_Guru": max(math.ceil(total / rasio_guru), 6)})
        prev = total
    return {"best_model": best, "eval_df": ev, "forecast_df": pd.DataFrame(rows)}
