"""Simulation response metrics for tuning evaluation."""

import pandas as pd


def compute_metrics(df: pd.DataFrame, setpoint: float) -> dict[str, float]:
    sp = float(setpoint)
    final_temp = float(df["temperature"].iloc[-1])
    max_temp = float(df["temperature"].max())
    overshoot_percent = max(0.0, (max_temp - sp) / sp * 100) if sp > 0 else 0.0

    return {
        "final_temperature": final_temp,
        "overshoot_percent": overshoot_percent,
        "steady_state_error": sp - final_temp,
    }
