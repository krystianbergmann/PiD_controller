"""Pydantic models for API request/response and OpenAPI documentation."""

from pydantic import BaseModel, ConfigDict, Field


class SimulationRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "setpoint": 80.0,
                    "initial_temp": 20.0,
                    "kp": 5.0,
                    "ki": 0.5,
                    "kd": 1.0,
                    "duration": 300.0,
                    "dt": 0.5,
                }
            ]
        }
    )

    setpoint: float = Field(..., description="Target temperature SP [°C]")
    initial_temp: float = Field(20.0, description="Starting process variable PV [°C]")
    kp: float = Field(5.0, ge=0, description="Proportional gain")
    ki: float = Field(0.5, ge=0, description="Integral gain")
    kd: float = Field(1.0, ge=0, description="Derivative gain")
    duration: float = Field(300.0, ge=60, le=600, description="Simulation length [s]")
    dt: float = Field(0.5, gt=0, description="Time step [s]")


class SimulationPoint(BaseModel):
    time: float
    temperature: float
    setpoint: float
    control: float
    error: float


class SimulationMetrics(BaseModel):
    final_temperature: float = Field(..., description="PV at end of run [°C]")
    overshoot_percent: float = Field(..., description="Peak above SP [%]")
    steady_state_error: float = Field(..., description="SP minus final PV [°C]")


class SimulationResponse(BaseModel):
    series: list[SimulationPoint]
    metrics: SimulationMetrics


class HealthResponse(BaseModel):
    status: str


class PlantDefaults(BaseModel):
    gain: float = Field(..., description="Plant gain K")
    time_constant: float = Field(..., description="Time constant T [s]")
    delay: float = Field(..., description="Transport delay L [s]")
    ambient: float = Field(..., description="Ambient temperature [°C]")
