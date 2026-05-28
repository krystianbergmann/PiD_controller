"""Streamlit app for PID controller tuning (temperature)."""

import plotly.graph_objects as go
import streamlit as st

from metrics import compute_metrics
from simulation import run_simulation

st.set_page_config(
    page_title="PID – temperature tuning",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.title("PID tuning – temperature control")
st.caption("Step-response simulation for a setpoint change.")

with st.expander("Guide: what is what?", expanded=False):
    st.markdown(
        """
        **Control loop (simulated)**  
        You set a **target temperature** → the **PID controller** drives a **heater (0–100%)** →
        a **thermal model** updates the **actual temperature** → the controller reacts again each step.

        | Part | Where | Meaning |
        |------|--------|---------|
        | **Setpoint (SP)** | Parameters → *Setpoint temperature* | Temperature you want to reach |
        | **Process variable (PV)** | Chart → blue line | Actual temperature over time |
        | **SP on chart** | Chart → red dashed line | Same as Ū (constant target) |
        | **Kp, Ki, Kd** | Parameters → PID sliders | How aggressively the heater responds |
        | **Initial temperature** | Parameters | Starting PV before heating (e.g. room temp) |
        | **Simulation time** | Parameters | How many seconds the run lasts |

        **Metrics (below the chart)**  
        - **Final temperature** — PV at the end (should be close to SP)  
        - **Overshoot** — how much PV went *above* SP before settling (%)  
        - **Steady-state error** — SP minus final PV (should be near 0 with good Ki)  
        - **Settling time (±2%)** — when PV enters the band around SP and stays there
        """
    )

st.header("Parameters")
temp_col1, temp_col2, temp_col3 = st.columns(3)
with temp_col1:
    setpoint = st.number_input(
        "Setpoint temperature [°C]",
        value=25.0,
        step=1.0,
        help="Target (SP): the temperature the controller aims for.",
    )
with temp_col2:
    initial_temp = st.number_input(
        "Initial temperature [°C]",
        value=20.0,
        step=1.0,
        help="Starting PV before the simulated heater warms up.",
    )
with temp_col3:
    duration = st.slider(
        "Simulation time [s]",
        60,
        600,
        300,
        30,
        help="Length of the run in seconds.",
    )

st.subheader("PID gains")
pid_col1, pid_col2, pid_col3 = st.columns(3)
with pid_col1:
    kp = st.slider(
        "Kp (proportional)",
        0.0,
        50.0,
        5.0,
        0.1,
        help="Reacts to the current error (SP − PV). Main knob for speed.",
    )
    st.caption(
        "Higher Kp → stronger heater response and faster heating. "
        "Too high → overshoot or oscillation around the setpoint."
    )
with pid_col2:
    ki = st.slider(
        "Ki (integral)",
        0.0,
        10.0,
        0.5,
        0.05,
        help="Removes error that stays over time (steady-state offset).",
    )
    st.caption(
        "Higher Ki → less leftover gap at the end. "
        "Too high → overshoot, slow wobble, or integral wind-up in real systems."
    )
with pid_col3:
    kd = st.slider(
        "Kd (derivative)",
        0.0,
        20.0,
        1.0,
        0.1,
        help="Reacts to how fast the error is changing; brakes sharp moves.",
    )
    st.caption(
        "Higher Kd → smoother approach, can reduce overshoot. "
        "Too high → sluggish response; on real sensors, amplifies noise."
    )

_, btn_col, _ = st.columns([1, 1, 1])
with btn_col:
    run = st.button("Run simulation", type="primary", use_container_width=True)

if run:
    st.session_state["df"] = run_simulation(
        setpoint=setpoint,
        kp=kp,
        ki=ki,
        kd=kd,
        duration=float(duration),
        initial_temp=initial_temp,
    )

st.header("Results")

if "df" in st.session_state:
    df = st.session_state["df"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["temperature"],
            name="Temperature (PV)",
            line=dict(color="#1f77b4", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["setpoint"],
            name="Setpoint (SP)",
            line=dict(color="#d62728", width=2, dash="dash"),
        )
    )
    fig.update_layout(
        title="Tuning response",
        xaxis_title="Time [s]",
        yaxis_title="Temperature [°C]",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Blue = actual temperature (PV). Red dashed = target (SP). "
        "Gap between them is the error the PID tries to remove."
    )

    sp = float(df["setpoint"].iloc[0])
    m = compute_metrics(df, sp)

    settling = m["settling_time_s"]
    settling_label = f"{settling:.1f} s" if settling is not None else "Not reached"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Final temperature", f"{m['final_temperature']:.1f} °C")
    col2.metric("Overshoot", f"{m['overshoot_percent']:.1f} %")
    col3.metric("Steady-state error", f"{m['steady_state_error']:.2f} °C")
    col4.metric("Settling time (±2%)", settling_label)
else:
    st.info("Adjust the parameters above and click **Run simulation**.")
