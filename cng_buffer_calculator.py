import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🔁 Cascade CNG Simulation: 1 Vehicle | LP → MP → HP")

# --- Configuration
P_nozzle_min = st.number_input("Target vehicle pressure (bar)", value=200.0)
delta_p_min = st.number_input("Minimum ΔP to transfer (bar)", value=5.0)

# Bank pressures
P_LP_init = st.number_input("Initial LP pressure", value=100.0)
P_MP_init = st.number_input("Initial MP pressure", value=150.0)
P_HP_init = st.number_input("Initial HP pressure", value=250.0)

# Bank volumes
V_LP = st.number_input("LP buffer volume (m³)", value=2.0)
V_MP = st.number_input("MP buffer volume (m³)", value=2.0)
V_HP = st.number_input("HP buffer volume (m³)", value=2.0)

# Vehicle volume
V_vehicle = st.number_input("Vehicle volume (m³)", value=0.3)

# Step size for simulation
step_time = 1  # minutes
max_time = 30  # min

if st.button("🚀 Run Simulation"):

    # Initialization
    time_series = []
    P_vehicle_series = []
    P_LP_series = []
    P_MP_series = []
    P_HP_series = []

    P_LP = P_LP_init
    P_MP = P_MP_init
    P_HP = P_HP_init
    P_veh = 1.0  # bar atmospheric pressure

    i = 0
    while i < max_time and P_veh < P_nozzle_min:

        current_bank = None
        if P_LP - P_veh >= delta_p_min:
            current_bank = "LP"
        elif P_MP - P_veh >= delta_p_min:
            current_bank = "MP"
        elif P_HP - P_veh >= delta_p_min:
            current_bank = "HP"
        else:
            st.warning("❌ No bank has enough pressure to continue filling.")
            break

        # Gas transfer for this minute (simplified)
        delta_p = 0
        if current_bank == "LP":
            delta_p = P_LP - P_veh
            transferred = min(V_LP, (delta_p / P_LP) * V_LP * 0.05)
            P_LP -= (transferred / V_LP) * P_LP
        elif current_bank == "MP":
            delta_p = P_MP - P_veh
            transferred = min(V_MP, (delta_p / P_MP) * V_MP * 0.05)
            P_MP -= (transferred / V_MP) * P_MP
        elif current_bank == "HP":
            delta_p = P_HP - P_veh
            transferred = min(V_HP, (delta_p / P_HP) * V_HP * 0.05)
            P_HP -= (transferred / V_HP) * P_HP

        # Vehicle pressure rise (simplified)
        if transferred > 0:
            P_veh += (transferred / V_vehicle) * P_veh * 0.04
            P_veh = min(P_veh, P_nozzle_min)

        # Log
        time_series.append(i)
        P_vehicle_series.append(P_veh)
        P_LP_series.append(P_LP)
        P_MP_series.append(P_MP)
        P_HP_series.append(P_HP)

        i += step_time

    # --- Plot
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(time_series, P_vehicle_series, label="Vehicle")
    ax.plot(time_series, P_LP_series, label="LP bank")
    ax.plot(time_series, P_MP_series, label="MP bank")
    ax.plot(time_series, P_HP_series, label="HP bank")
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Pressure (bar)")
    ax.set_title("📈 Pressures during cascade refueling")
    ax.legend()
    st.pyplot(fig)

    st.success("✅ Simulation complete.")
