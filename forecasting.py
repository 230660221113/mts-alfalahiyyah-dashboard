import math
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA


def _metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    nonzero = y_true != 0
    mape = float(np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100) if np.any(nonzero) else 0.0
    return {"MAE": round(mae, 2), "RMSE": round(rmse, 2), "MAPE": round(mape, 2)}


def run_auto_forecast(df_hist: pd.DataFrame, horizon: int = 2, kapasitas_rombel: int = 32, rasio_guru: int = 20) -> dict:
    """
    Menjalankan 4 algoritma peramalan (Linear Regression, Holt Exponential Smoothing,
    ARIMA, dan Random Forest) di belakang layar, mengevaluasi galatnya (MAPE/RMSE),
    dan secara otomatis memilih model terbaik untuk disajikan ke Operator & Kepala Sekolah.
    """
    df = df_hist.sort_values("tahun_mulai").reset_index(drop=True)
    y = df["total_aktif"].astype(float).values
    n = len(y)
    X = np.arange(n).reshape(-1, 1)
    X_future = np.arange(n, n + horizon).reshape(-1, 1)

    candidates = {}

    # 1. Regresi Linier
    lr = LinearRegression().fit(X, y)
    candidates["Regresi Linier"] = (lr.predict(X), lr.predict(X_future))

    # 2. Holt's Exponential Smoothing
    try:
        holt = ExponentialSmoothing(y, trend="add", damped_trend=True).fit()
        candidates["Holt Exponential Smoothing"] = (holt.fittedvalues, holt.forecast(horizon))
    except Exception:
        pass

    # 3. ARIMA(1,1,0)
    try:
        arima = ARIMA(y, order=(1, 1, 0)).fit()
        candidates["ARIMA"] = (arima.fittedvalues, arima.forecast(horizon))
    except Exception:
        pass

    # 4. Random Forest Regressor
    try:
        rf = RandomForestRegressor(n_estimators=100, random_state=42).fit(X, y)
        candidates["Random Forest"] = (rf.predict(X), rf.predict(X_future))
    except Exception:
        pass

    eval_table = []
    best_name = "Regresi Linier"
    best_score = float("inf")

    for name, (fit_vals, fut_vals) in candidates.items():
        m = _metrics(y, np.asarray(fit_vals))
        eval_table.append({"Algoritma": name, **m})
        # Skor gabungan MAPE & RMSE untuk pemilihan otomatis di latar belakang
        score = m["MAPE"] + (m["RMSE"] * 0.1)
        if score < best_score:
            best_score = score
            best_name = name

    _, best_future = candidates[best_name]
    best_future = np.maximum(np.round(best_future), 0).astype(int)

    # Susun tabel proyeksi per tahun ajaran mendatang + kebutuhan rombel & guru
    last_start = int(df["tahun_mulai"].iloc[-1])
    last_total = int(df["total_aktif"].iloc[-1])

    # Proporsi historis rata-rata per tingkat (VII, VIII, IX) untuk estimasi distribusi kelas
    p_vii = float((df["kelas_vii"] / df["total_aktif"].replace(0, np.nan)).mean())
    p_viii = float((df["kelas_viii"] / df["total_aktif"].replace(0, np.nan)).mean())
    if np.isnan(p_vii) or np.isnan(p_viii):
        p_vii, p_viii = 0.35, 0.33

    proj_rows = []
    prev_val = last_total
    for step in range(1, horizon + 1):
        s_yr = last_start + step
        e_yr = s_yr + 1
        ta_label = f"{s_yr}/{e_yr}"
        pred_total = int(best_future[step - 1])
        est_vii = int(round(pred_total * p_vii))
        est_viii = int(round(pred_total * p_viii))
        est_ix = max(pred_total - est_vii - est_viii, 0)

        rombel_butuh = max(math.ceil(pred_total / kapasitas_rombel), 3)
        guru_butuh = max(math.ceil(pred_total / rasio_guru), 6)
        delta = pred_total - prev_val
        prev_val = pred_total

        proj_rows.append({
            "Tahun_Ajaran": ta_label,
            "Proyeksi_Siswa_Aktif": pred_total,
            "Est_Kelas_VII": est_vii,
            "Est_Kelas_VIII": est_viii,
            "Est_Kelas_IX": est_ix,
            "Perubahan": f"{delta:+d} siswa",
            "Kebutuhan_Rombel": rombel_butuh,
            "Kebutuhan_Guru": guru_butuh,
        })

    return {
        "best_model": best_name,
        "eval_df": pd.DataFrame(eval_table).sort_values("MAPE"),
        "forecast_df": pd.DataFrame(proj_rows),
    }
