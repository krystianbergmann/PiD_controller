# PID – temperature tuning

## TL;DR

**What it is:** A small web app that **pretends to heat something** (like an oven) and shows whether your PID settings are any good. A **REST API** with Swagger UI at `/docs` runs the same simulation for scripts and integrations.

**What you do:** Pick a target temperature, move three sliders (**Kp**, **Ki**, **Kd**), click **Run simulation**, and read the graph.

**What you see:** A blue line (actual temperature) chasing a red dashed line (target). Four metrics below the chart: final temperature, overshoot, steady-state error, and **settling time** (±2% of the step).

**Why it exists:** Tuning on real hardware is slow and risky. Here everything is **math in Python** — fast, safe, good for learning and portfolio demos.

**What it is not:** It does not talk to a real sensor or heater. Gains from the app are a **starting point for intuition**, not a factory-ready recipe.

---

A simple Python (Streamlit) app to **simulate and visualize** PID tuning for temperature control. It helps you see how controller gains affect heating behavior **before** touching real hardware.

## The problem

Many systems must hold a **target temperature** (setpoint): ovens, 3D printer beds, chemical reactors, HVAC zones, and more.

You typically have:

| Role | Meaning | Example |
|------|---------|---------|
| **Setpoint (SP)** | Desired temperature | 80 °C |
| **Process variable (PV)** | Measured temperature | 72 °C |
| **Control output (u)** | Actuator command | Heater power 0–100% |

The difficulty: temperature **does not change instantly**. Heat spreads with **delay**, and the object has **inertia** (thermal mass). If you apply full power too long, you **overshoot** the target; if you stop too early, you **undershoot** and drift. A fixed “on/off at 80 °C” rule often **oscillates** or reacts too slowly.

**Tuning** means choosing controller parameters so the system reaches SP **quickly**, with **acceptable overshoot**, and **little steady error** — without unsafe oscillation.

## Solution space

There are many ways to solve “hold this temperature.” This project sits in one corner of that space:

| Approach | Idea | This project |
|----------|------|----------------|
| **Bang-bang (on/off)** | Full power on/off at a threshold | Not implemented (often oscillates around SP) |
| **PID control** | Continuous u from error and its integral/derivative | **Yes** — core of the app |
| **Model-based / MPC** | Use a detailed model to optimize u | Not implemented (more complex) |
| **Manual tuning on hardware** | Change gains on the real plant | **Simulated first** — safer and faster for learning |
| **Rule-based tuning (e.g. Ziegler–Nichols)** | Formulas from step tests | Not automated (you tune sliders by hand) |

**Why PID?** It is widely used in industry, easy to explain, and maps well to a portfolio demo: a few knobs (**Kp**, **Ki**, **Kd**) with a clear plot.

**Why simulation?** Real experiments cost time, energy, and risk equipment. A **software plant** (mathematical model) lets you run many “what if” scenarios in seconds. This repo is for **learning and visualization**, not for deploying to a factory line as-is.

## What this app does (and does not do)

**Does:**

- Simulates a **closed loop**: PID → heater command → thermal model → temperature → back to PID.
- Lets you set **SP**, initial temperature, **Kp / Ki / Kd**, and simulation length.
- Plots **PV vs SP** and shows **overshoot**, **steady-state error**, and **settling time**.
- **Streamlit UI** with in-app guide and PID slider hints; parameters in the main panel (not the sidebar).

**Does not:**

- Connect to real sensors or actuators (no serial, MQTT, PLC).
- Guarantee optimal or safe gains for your physical device.
- Model every real effect (noise, sensor lag, multi-zone heat, cooling fans, etc.).

Treat results as **qualitative guidance**: “more Kp → faster but more overshoot,” not as final production parameters.

## How it works

### Closed-loop idea

Each time step (default **0.5 s**):

1. Read current temperature **PV**.
2. Compute error: **e = SP − PV**.
3. PID computes **u** (0–100%, e.g. heater duty).
4. The **thermal plant** updates PV from **u**.
5. Repeat until the simulation ends.

```
  Setpoint (SP) ──►  PID  ──►  u  ──►  Thermal plant  ──►  Temperature (PV)
       ▲                                                    │
       └────────────────── feedback ─────────────────────────┘
```

### Modules

| File | Role |
|------|------|
| `pid_controller.py` | PID with output limits and anti-windup (stops integral wind-up when u is saturated). |
| `plant.py` | Simple thermal model: inertia (first order) + delay, plus ambient temperature. |
| `simulation.py` | Runs the loop; returns time, temperature, setpoint, control, error. |
| `metrics.py` | Tuning metrics: overshoot, steady-state error, settling time (±2% of step). |
| `app.py` | Streamlit UI, plot, and metrics display. |
| `api/main.py` | REST API (`/health`, `/simulate`, `/plant/defaults`) with Swagger at `/docs`. |

### PID parameters (what to turn)

| Gain | Effect (intuition) |
|------|---------------------|
| **Kp** | Stronger reaction to current error → faster rise; too high → overshoot / oscillation. |
| **Ki** | Fixes persistent offset (PV stuck below SP); too high → overshoot or slow oscillation. |
| **Kd** | Dampens fast changes; can reduce overshoot; less critical in this smooth simulation. |

### Plant model (what is being “heated”)

The default plant behaves like a sluggish heater:

- **Inertia** — temperature approaches a target gradually (not a step jump).
- **Delay** — control action affects temperature only after a few seconds.
- **Ambient** — system is pulled toward ~20 °C when heating is low.

Defaults (gain 0.8, τ ≈ 30 s, delay 5 s) are a **reasonable teaching example**, not a calibrated model of your specific oven.

### Metrics on the chart

| Metric | Meaning |
|--------|---------|
| **Final temperature** | PV at end of run — should be near SP. |
| **Overshoot** | Peak above SP (%) — lower is often better for delicate processes. |
| **Steady-state error** | SP − final PV — should be near zero if Ki is adequate. |
| **Settling time (±2%)** | First time PV stays within ±2% of the step (SP − start) until the end [s]; “Not reached” if the run is too short. |

### Suggested tuning workflow

1. Set **SP** and **initial temperature** (e.g. 20 → 80 °C step).
2. Increase **Kp** until the response is reasonably fast without heavy oscillation.
3. Add **Ki** to remove remaining offset; back off if overshoot grows.
4. Add **Kd** only if you still need less overshoot.
5. Compare runs using the plot and metrics; increase **simulation time** if settling time shows “Not reached”.
6. Optionally call the same simulation via **POST /simulate** (API) for scripts or automation.

### Settling time (how it is calculated)

**Settling time** is when PV enters a band around SP and **does not leave it** until the end of the run:

- Tolerance = **2% × |SP − initial temperature|** (based on step size, not % of SP alone).
- If PV is still outside the band at the last sample, the metric is **not reached** (`null` in the API, “Not reached” in the UI).

## Features

- Temperature control with **Kp**, **Ki**, **Kd**
- Step-response simulation (setpoint vs. actual temperature)
- Tuning plot (Plotly)
- Basic metrics: overshoot, steady-state error, settling time
- REST API with auto-generated **Swagger** documentation

## Requirements

- Python 3.11+

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

**Streamlit UI:**

```bash
streamlit run app.py
```

**REST API (Swagger at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)):**

```bash
uvicorn api.main:app --reload --port 8000
```

| URL | Description |
|-----|-------------|
| `/docs` | Swagger UI (try endpoints in the browser) |
| `/redoc` | ReDoc API reference |
| `/openapi.json` | OpenAPI schema |

### API functions (simple reference)

The API runs the **same simulation** as the Streamlit app and returns **JSON** instead of a chart. Use it from scripts, other apps, or the interactive docs at `/docs`.

#### `GET /health`

Checks that the API server is running.

- **Use when:** deploying, monitoring, or verifying the service is up.
- **Response:** `{"status": "ok"}`

#### `GET /plant/defaults`

Returns the default parameters of the **simulated thermal plant** (the “oven” model).

- **Use when:** you want to know what inertia, delay, and ambient temperature the simulator assumes.
- **Response fields:**
  - `gain` — how strongly heater power affects temperature
  - `time_constant` — how slowly temperature changes [s]
  - `delay` — lag before control affects temperature [s]
  - `ambient` — surrounding temperature [°C] (default 20)

#### `POST /simulate`

Runs one **closed-loop PID simulation**: controller + plant from initial temperature toward the setpoint.

- **Use when:** you need the full time series or tuning metrics programmatically.
- **Request body (JSON):**

| Field | Meaning | Typical value |
|-------|---------|----------------|
| `setpoint` | Target temperature SP [°C] | `80` |
| `initial_temp` | Starting temperature PV [°C] | `20` |
| `kp`, `ki`, `kd` | PID gains (≥ 0) | `5`, `0.5`, `1` |
| `duration` | Run length [s], 60–600 | `300` |
| `dt` | Time step [s] | `0.5` |

- **Response:**
  - `series` — list of steps, each with `time`, `temperature` (PV), `setpoint` (SP), `control` (heater 0–100%), `error`
  - `metrics` — summary for tuning:
    - `final_temperature` — PV at the end [°C]
    - `overshoot_percent` — how far PV peaked above SP [%]
    - `steady_state_error` — SP minus final PV [°C] (should be small with good Ki)
    - `settling_time_s` — settling time [s], or `null` if not settled before `duration` ends

**Example request:**

```bash
curl -X POST http://127.0.0.1:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{"setpoint":80,"initial_temp":20,"kp":5,"ki":0.5,"kd":1,"duration":300,"dt":0.5}'
```

### Tests

```bash
pytest tests/ -v
```

Covers API smoke tests (`test_api.py`) and metrics logic including settling time (`test_metrics.py`).

## Project structure

```
.
├── api/
│   ├── main.py         # FastAPI app and routes
│   └── schemas.py      # Pydantic models (OpenAPI / Swagger)
├── app.py              # Streamlit UI
├── metrics.py          # overshoot, steady-state error, settling time
├── pid_controller.py   # PID controller
├── plant.py            # thermal plant model
├── simulation.py       # simulation loop
├── tests/
│   ├── test_api.py
│   └── test_metrics.py
├── requirements.txt
└── README.md
```

## License

MIT
