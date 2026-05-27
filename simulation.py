"""Symulacja pętli regulacji temperatury."""

import pandas as pd

from pid_controller import PIDController
from plant import ThermalPlant


def run_simulation(
    setpoint: float,
    kp: float,
    ki: float,
    kd: float,
    duration: float = 300.0,
    dt: float = 0.5,
    initial_temp: float = 20.0,
) -> pd.DataFrame:
    steps = int(duration / dt)
    controller = PIDController(kp=kp, ki=ki, kd=kd)
    plant = ThermalPlant(dt=dt)
    plant.reset(initial_temp)

    records: list[dict[str, float]] = []
    for i in range(steps):
        pv = plant.pv
        u = controller.step(setpoint, pv, dt)
        pv = plant.step(u)
        records.append(
            {
                "time": i * dt,
                "temperature": pv,
                "setpoint": setpoint,
                "control": u,
                "error": setpoint - pv,
            }
        )

    return pd.DataFrame(records)
