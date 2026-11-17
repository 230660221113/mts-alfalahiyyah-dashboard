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
    return ExponentialSmoothing(y, trend="add", initialization_method="estimated").fit().forecast(h)

def _arima(y, h):
    return ARIMA(y, order=(1, 1, 0)).fit().forecast(h)

def _rf(y, h, lags=2):
    y = [float(v) for v in y]
    X = [y[i - lags:i] for i in range(lags, len(y))]
    m = RandomForestRegressor(n_estimators=200, random_state=42).fit(X, y[lags:])
    hist, out = y[:], []
    for _ in range(h):  # rekursif
        p = m.predict([hist[-lags:]])[0]
        out.append(p)
        hist.append(p)
    return np.array(out)

MODELS = {"Linear Regression": _lr, "Holt's Exponential Smoothing": _holt, "ARIMA": _arima, "Random Forest": _rf}

def evaluate(y, n_test=2) -> pd.DataFrame:
    y = np.asarray(y, float)
    train, test = y[:-n_test], y[-n_test:]
    rows = []
    for name, fn in MODELS.items():
        try:
            e = test - np.asarray(fn(train, n_test))
            rows.append({"Model": name, "MAE": np.mean(abs(e)), "RMSE": np.sqrt(np.mean(e**2)), "MAPE (%)": np.mean(abs(e / test)) * 100})
        except Exception:
            continue
    return pd.DataFrame(rows).sort_values("MAPE (%)").reset_index(drop=True)

def forecast(y, horizon):
    y = np.asarray(y, float)
    metrics = evaluate(y)
    best = metrics.iloc[0]["Model"]
    return best, np.asarray(MODELS[best](y, horizon)), metrics

def next_years(last: str, h: int) -> list[str]:
    a = int(last.split("/")[0])
    return [f"{a + i}/{a + i + 1}" for i in range(1, h + 1)]
