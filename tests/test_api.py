"""Smoke tests for the FastAPI service."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_plant_defaults() -> None:
    response = client.get("/plant/defaults")
    assert response.status_code == 200
    data = response.json()
    assert "gain" in data
    assert "time_constant" in data
    assert "delay" in data
    assert "ambient" in data


def test_simulate() -> None:
    payload = {
        "setpoint": 80.0,
        "initial_temp": 20.0,
        "kp": 5.0,
        "ki": 0.5,
        "kd": 1.0,
        "duration": 300.0,
        "dt": 0.5,
    }
    response = client.post("/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["series"]) > 0
    metrics = data["metrics"]
    assert "final_temperature" in metrics
    assert "overshoot_percent" in metrics
    assert "steady_state_error" in metrics
