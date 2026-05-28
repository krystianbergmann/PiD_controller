"""Simulation response metrics for tuning evaluation."""

import pandas as pd


def settling_time(
    df: pd.DataFrame,
    setpoint: float,
    tolerance_percent: float = 2.0,
) -> float | None:
    """Time when PV enters ±tolerance% of the step size band and stays until end.

    tolerance is applied to |SP - PV0| (the step magnitude), not |SP|.
    Returns None if the response never settles before the simulation ends.
    """
    sp = float(setpoint)
    pv = df["temperature"].tolist()
    times = df["time"].tolist()
    tol = (tolerance_percent / 100.0) * abs(sp - pv[0])
    if tol <= 1e-9:
        return 0.0

    outside = [abs(p - sp) > tol for p in pv]
    if not any(outside):
        return 0.0

    last_outside = max(i for i, out in enumerate(outside) if out)
    if last_outside == len(outside) - 1:
        return None

    return float(times[last_outside + 1])


def compute_metrics(
    df: pd.DataFrame,
    setpoint: float,
    tolerance_percent: float = 2.0,
) -> dict[str, float | None]:
    sp = float(setpoint)
    final_temp = float(df["temperature"].iloc[-1])
    max_temp = float(df["temperature"].max())
    overshoot_percent = max(0.0, (max_temp - sp) / sp * 100) if sp > 0 else 0.0

    return {
        "final_temperature": final_temp,
        "overshoot_percent": overshoot_percent,
        "steady_state_error": sp - final_temp,
        "settling_time_s": settling_time(df, sp, tolerance_percent),
    }
