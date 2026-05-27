# PID – temperature tuning

A simple Python (Streamlit) app to simulate and visualize PID controller tuning for a thermal process.

## Features

- Temperature control with **Kp**, **Ki**, **Kd** parameters
- Step-response simulation (setpoint vs. actual temperature)
- Tuning plot (Plotly)
- Basic metrics: overshoot, steady-state error

## Requirements

- Python 3.11+

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Project structure

```
.
├── app.py              # Streamlit UI
├── pid_controller.py   # PID controller
├── plant.py            # thermal plant model
├── simulation.py       # simulation loop
├── requirements.txt
└── README.md
```

## License

MIT
