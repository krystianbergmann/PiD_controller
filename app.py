"""Aplikacja Streamlit do strojenia regulatora PID (temperatura)."""

import plotly.graph_objects as go
import streamlit as st

from simulation import run_simulation

st.set_page_config(page_title="PID – strojenie temperatury", layout="wide")
st.title("Strojenie PID – regulacja temperatury")
st.caption("Symulacja odpowiedzi skokowej na zmianę temperatury zadanej.")

with st.sidebar:
    st.header("Parametry")
    setpoint = st.number_input("Temperatura zadana [°C]", value=80.0, step=1.0)
    initial_temp = st.number_input("Temperatura początkowa [°C]", value=20.0, step=1.0)
    kp = st.slider("Kp", 0.0, 50.0, 5.0, 0.1)
    ki = st.slider("Ki", 0.0, 10.0, 0.5, 0.05)
    kd = st.slider("Kd", 0.0, 20.0, 1.0, 0.1)
    duration = st.slider("Czas symulacji [s]", 60, 600, 300, 30)
    run = st.button("Uruchom symulację", type="primary")

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
            name="Temperatura (PV)",
            line=dict(color="#1f77b4", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["setpoint"],
            name="Temperatura zadana (SP)",
            line=dict(color="#d62728", width=2, dash="dash"),
        )
    )
    fig.update_layout(
        title="Wykres strojenia",
        xaxis_title="Czas [s]",
        yaxis_title="Temperatura [°C]",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    sp = float(df["setpoint"].iloc[0])
    final_temp = df["temperature"].iloc[-1]
    max_temp = df["temperature"].max()
    overshoot = max(0.0, (max_temp - sp) / sp * 100) if sp > 0 else 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("Temperatura końcowa", f"{final_temp:.1f} °C")
    col2.metric("Przeregulowanie", f"{overshoot:.1f} %")
    col3.metric("Błąd ustalony", f"{sp - final_temp:.2f} °C")
else:
    st.info("Ustaw parametry w panelu bocznym i kliknij **Uruchom symulację**.")
