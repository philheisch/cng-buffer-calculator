import streamlit as st

# Title
st.title("🔧 CNG Buffer Storage Calculator")

# User inputs
st.header("Input Parameters")
Q_d = st.number_input("Downstream Flow (Nm³/h)", min_value=0.0, step=1.0)
N = st.number_input("Number of Refueling Nozzles", min_value=1, step=1)
Q_n = st.number_input("Flow per Nozzle (Nm³/min)", min_value=0.0, step=0.1)
t_refuel = st.number_input("Refueling Time (min)", min_value=0.0, step=0.1)
P_max = st.number_input("Maximum Buffer Pressure (bar)", min_value=1.0, step=0.1)
P_min = st.number_input("Minimum Pressure Allowed at Nozzle (bar)", min_value=0.0, step=0.1)
safety_factor = st.number_input("Safety Margin (%)", min_value=0.0, value=10.0, step=1.0)

# Calculation
if st.button("Calculate Required Buffer Volume"):
    if P_max > P_min and Q_n > 0 and N > 0 and t_refuel > 0:
        P_atm = 1.013  # bar
        Q_total = N * Q_n * t_refuel  # Nm³
        usable_pressure_diff = P_max - P_min  # bar
        V_buffer = Q_total * P_atm / usable_pressure_diff  # m³ at P_max
        V_buffer_final = V_buffer * (1 + safety_factor / 100)

        st.success("✅ Calculation Complete")
        st.write(f"• Total Gas Needed: {Q_total:.2f} Nm³")
        st.write(f"• Required Buffer Volume (at high pressure): {V_buffer_final:.2f} m³")
        st.write(f"• Equivalent Volume at 1 bar: {(V_buffer_final * usable_pressure_diff / P_atm):.2f} m³")
    else:
        st.error("Please make sure all inputs are valid and P_max > P_min.")
