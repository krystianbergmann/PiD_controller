"""Streamlit app for PID controller tuning (temperature)."""

import plotly.graph_objects as go
import streamlit as st

from simulation import run_simulation

st.set_page_config(page_title="PID – temperature tuning", layout="wide")
st.title("PID tuning – temperature control")
st.caption("Step-response simulation for a setpoint change.")

with st.sidebar:
    st.header("Parameters")
    setpoint = st.number_input("Setpoint temperature [°C]", value=80.0, step=1.0)
    initial_temp = st.number_input("Initial temperature [°C]", value=20.0, step=1.0)
    kp = st.slider("Kp", 0.0, 50.0, 5.0, 0.1)
    ki = st.slider("Ki", 0.0, 10.0, 0.5, 0.05)
    kd = st.slider("Kd", 0.0, 20.0, 1.0, 0.1)
    duration = st.slider("Simulation time [s]", 60, 600, 300, 30)
    run = st.button("Run simulation", type="primary")

if run:
    st.session_state["df"] = run_simulation(
        setpoint=setpoint,
        kp=kp,
        ki=ki,
        kd=kd,
        duration=float(duration),
        initial_temp=initial_temp,
    )

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

    sp = float(df["setpoint"].iloc[0])
    final_temp = df["temperature"].iloc[-1]
    max_temp = df["temperature"].max()
    overshoot = max(0.0, (max_temp - sp) / sp * 100) if sp > 0 else 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("Final temperature", f"{final_temp:.1f} °C")
    col2.metric("Overshoot", f"{overshoot:.1f} %")
    col3.metric("Steady-state error", f"{sp - final_temp:.2f} °C")
else:
    st.info("Set parameters in the sidebar and click **Run simulation**.")
