"""Empat model peramalan deret waktu tahunan. Setiap fungsi: (y: array, h: int) -> array(h)."""
from __future__ import annotations

import warnings

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    HAS_STATSMODELS = True
except ImportError:  # pragma: no cover
    HAS_STATSMODELS = False


def linear_regression(y, h: int) -> np.ndarray:
    y = np.asarray(y, float)
    X = np.arange(len(y)).reshape(-1, 1)
    m = LinearRegression().fit(X, y)
    return m.predict(np.arange(len(y), len(y) + h).reshape(-1, 1))


def holt(y, h: int) -> np.ndarray:
    y = np.asarray(y, float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = ExponentialSmoothing(y, trend="add", initialization_method="estimated").fit()
    return np.asarray(fit.forecast(h))


def arima(y, h: int) -> np.ndarray:
    """ARIMA(p,1,q) dengan grid kecil, dipilih berdasarkan AIC (cocok untuk deret pendek)."""
    y = np.asarray(y, float)
    best, best_aic = None, np.inf
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for p in (0, 1, 2):
            for q in (0, 1):
                for trend in ("t", "n"):
                    try:
                        res = ARIMA(y, order=(p, 1, q), trend=trend).fit()
                    except Exception:
                        continue
                    if np.isfinite(res.aic) and res.aic < best_aic:
                        best, best_aic = res, res.aic
    if best is None:
        raise ValueError("ARIMA gagal dipasang pada data ini.")
    return np.asarray(best.forecast(h))


def random_forest(y, h: int, window: int = 2, seed: int = 42) -> np.ndarray:
    """Random Forest pada selisih antar-tahun (agar tidak datar di luar rentang data latih)."""
    y = np.asarray(y, float)
    d = np.diff(y)
    w = min(window, len(d) - 2)
    if w < 1:
        raise ValueError("Data terlalu pendek untuk Random Forest.")
    X = np.array([d[i - w:i] for i in range(w, len(d))])
    model = RandomForestRegressor(n_estimators=200, random_state=seed).fit(X, d[w:])
    hist, last, out = list(d), y[-1], []
    for _ in range(h):
        step = float(model.predict(np.array([hist[-w:]]))[0])
        hist.append(step)
        last += step
        out.append(last)
    return np.array(out)


MODELS = {
    "Linear Regression": linear_regression,
    "Holt's Exponential Smoothing": holt,
    "ARIMA": arima,
    "Random Forest": random_forest,
}
NEEDS_STATSMODELS = {"Holt's Exponential Smoothing", "ARIMA"}


def available_models() -> dict:
    return {k: v for k, v in MODELS.items() if HAS_STATSMODELS or k not in NEEDS_STATSMODELS}
