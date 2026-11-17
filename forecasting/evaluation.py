"""Evaluasi komparatif model: backtest expanding-window satu langkah, metrik MAE/RMSE/MAPE."""
from __future__ import annotations

import numpy as np
import pandas as pd

from forecasting.models import available_models

MIN_TRAIN = 4


def metrics(actual, pred) -> dict:
    a, p = np.asarray(actual, float), np.asarray(pred, float)
    err = a - p
    nz = a != 0
    return {
        "MAE": float(np.mean(np.abs(err))),
        "RMSE": float(np.sqrt(np.mean(err ** 2))),
        "MAPE (%)": float(np.mean(np.abs(err[nz] / a[nz])) * 100) if nz.any() else float("nan"),
    }


def backtest(y, fn, min_train: int = MIN_TRAIN) -> dict:
    y = np.asarray(y, float)
    preds, actual = [], []
    for i in range(min_train, len(y)):
        preds.append(float(fn(y[:i], 1)[0]))
        actual.append(y[i])
    if not preds:
        raise ValueError("Data terlalu pendek untuk backtest.")
    return metrics(actual, preds)


def compare_models(y) -> pd.DataFrame:
    """Tabel perbandingan model, terurut dari RMSE terkecil. Model gagal tetap ditampilkan."""
    rows = []
    for name, fn in available_models().items():
        try:
            rows.append({"Model": name, **backtest(y, fn), "Status": "OK"})
        except Exception as e:
            rows.append({"Model": name, "MAE": np.nan, "RMSE": np.nan, "MAPE (%)": np.nan,
                         "Status": f"Gagal: {e}"[:80]})
    return pd.DataFrame(rows).sort_values("RMSE", na_position="last").reset_index(drop=True)


def best_model(table: pd.DataFrame) -> str:
    ok = table[table["Status"] == "OK"]
    if ok.empty:
        raise ValueError("Tidak ada model yang berhasil dievaluasi.")
    return ok.iloc[0]["Model"]


def forecast(y, model: str, horizon: int) -> np.ndarray:
    return np.maximum(np.round(available_models()[model](np.asarray(y, float), horizon)), 0)
