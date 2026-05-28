"""Tests for simulation metrics."""

import pandas as pd

from metrics import compute_metrics, settling_time


def test_settling_time_already_at_setpoint() -> None:
    df = pd.DataFrame({"time": [0.0, 1.0], "temperature": [80.0, 80.0]})
    assert settling_time(df, 80.0) == 0.0


def test_settling_time_reaches_band() -> None:
    df = pd.DataFrame(
        {
            "time": [0.0, 1.0, 2.0, 3.0],
            "temperature": [20.0, 50.0, 79.0, 80.0],
        }
    )
    # step = 60, 2% tol = 1.2; |79-80| and |80-80| inside band from t=2
    assert settling_time(df, 80.0, tolerance_percent=2.0) == 2.0


def test_settling_time_never_settles() -> None:
    df = pd.DataFrame(
        {
            "time": [0.0, 1.0, 2.0],
            "temperature": [20.0, 40.0, 50.0],
        }
    )
    assert settling_time(df, 80.0) is None


def test_compute_metrics_includes_settling_time() -> None:
    df = pd.DataFrame(
        {
            "time": [0.0, 1.0],
            "temperature": [20.0, 80.0],
        }
    )
    m = compute_metrics(df, 80.0)
    assert "settling_time_s" in m
