"""FastAPI service for PID temperature simulation."""

from fastapi import FastAPI

from api.schemas import (
    HealthResponse,
    PlantDefaults,
    SimulationPoint,
    SimulationRequest,
    SimulationMetrics,
    SimulationResponse,
)
from metrics import compute_metrics
from plant import ThermalPlant
from simulation import run_simulation

app = FastAPI(
    title="PID Temperature Tuning API",
    description=(
        "Simulate a closed-loop PID temperature controller with an FOPDT thermal plant. "
        "Use /docs for interactive Swagger UI."
    ),
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Liveness check for deployments and monitoring."""
    return HealthResponse(status="ok")


@app.get("/plant/defaults", response_model=PlantDefaults, tags=["plant"])
def plant_defaults() -> PlantDefaults:
    """Default thermal plant parameters used by the simulator."""
    plant = ThermalPlant()
    return PlantDefaults(
        gain=plant.gain,
        time_constant=plant.time_constant,
        delay=plant.delay_steps * plant.dt,
        ambient=plant.ambient,
    )


@app.post(
    "/simulate",
    response_model=SimulationResponse,
    tags=["simulation"],
    summary="Run closed-loop PID simulation",
)
def simulate(req: SimulationRequest) -> SimulationResponse:
    """Run a step-response simulation and return the time series plus tuning metrics."""
    df = run_simulation(
        setpoint=req.setpoint,
        kp=req.kp,
        ki=req.ki,
        kd=req.kd,
        duration=req.duration,
        dt=req.dt,
        initial_temp=req.initial_temp,
    )
    raw_metrics = compute_metrics(df, req.setpoint)
    series = [SimulationPoint(**row) for row in df.to_dict(orient="records")]
    metrics = SimulationMetrics(**raw_metrics)
    return SimulationResponse(series=series, metrics=metrics)
