import numpy as np
import pytest
from forecasting import models
from forecasting.evaluation import best_model, compare_models, forecast, metrics

Y = [310, 318, 325, 331, 340, 349, 355, 364]

def test_metrics():
    m = metrics([100, 200], [110, 190])
    assert m["MAE"] == 10 and round(m["MAPE (%)"], 2) == 7.5

def test_linear_extrapolates():
    out = models.linear_regression(Y, 3)
    assert len(out) == 3 and out[0] > Y[-1]

def test_random_forest_shape():
    assert len(models.random_forest(Y, 3)) == 3

def test_compare_and_forecast():
    t = compare_models(Y)
    assert {"MAE", "RMSE", "MAPE (%)"} <= set(t.columns)
    f = forecast(Y, best_model(t), 3)
    assert len(f) == 3 and (f >= 0).all()

@pytest.mark.skipif(not models.HAS_STATSMODELS, reason="statsmodels tidak terpasang")
def test_statsmodels_models():
    assert len(models.holt(Y, 2)) == 2 and len(models.arima(Y, 2)) == 2
