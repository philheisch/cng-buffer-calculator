import streamlit as st

# -------------------------------
# Title and Input Section
# -------------------------------
st.title("🔧 CNG Buffer Storage Calculator with 3-Bank Cascade Optimization")

st.header("📥 Input Parameters")

# Basic Inputs
Q_d = st.number_input("Downstream Flow (Nm³/h)", min_value=0.0, value=0.0, step=1.0)
P_d = st.number_input("Downstream Line Pressure (bar)", min_value=0.0, value=0.0, step=0.1)

N = st.number_input("Number of Refueling Nozzles", min_value=1, step=1)
Q_n = st.number_input("Flow per Nozzle (Nm³/min)", min_value=0.0, step=0.1)
t_refuel = st.number_input("Refueling Time (min)", min_value=0.0, step=0.1)

P_nozzle_min = st.number_input("Minimum Pressure Required at Nozzle (bar)", min_value=0.1, value=100.0, step=1.0)

safety_factor = st.number_input("Safety Margin (%)", min_value=0.0, value=10.0, step=1.0)

# Optional cascade toggle
enable_cascade = st.checkbox("Enable 3-Bank Cascade Optimization")

if enable_cascade:
    st.subheader("3-Bank Pressures (in bar)")
    P_HP = st.number_input("High Pressure Bank (HP)", min_value=P_nozzle_min + 1, value=250)
    P_MP = st.number_input("Mid Pressure Bank (MP)", min_value=P_nozzle_min + 1, value=200)
    P_LP = st.number_input("Low Pressure Bank (LP)", min_value=P_nozzle_min + 1, value=150)

# -------------------------------
# Calculation
# -------------------------------
if st.button("🔍 Calculate Required Buffer Volume"):

    if Q_n <= 0 or N <= 0 or t_refuel <= 0:
        st.error("⚠️ Please enter all required parameters with valid positive values.")
    else:
        # Step 1: Total refueling demand
        Q_total = N * Q_n * t_refuel  # Nm³

        # Step 2: Downstream contribution (if pressure allows)
        Q_d_per_min = Q_d / 60
        downstream_gas = 0
        if P_d >= P_nozzle_min:
            downstream_gas = min(Q_d_per_min * t_refuel, Q_total)

        net_buffer_gas = Q_total - downstream_gas

        st.write(f"🔧 **Total Gas Needed at Nozzles:** {Q_total:.2f} Nm³")
        st.write(f"➖ Contribution from Downstream Line: {downstream_gas:.2f} Nm³")
        st.write(f"🧮 Net Gas to Supply from Buffer: {net_buffer_gas:.2f} Nm³")

        # Step 3: Cascade logic or basic 1-stage buffer
        P_atm = 1.013

        if enable_cascade:
            # Compute effective volume needed in each bank
            def bank_volume(V_needed, P_start, P_end):
                delta_P = P_start - P_end
                return (V_needed * P_atm) / delta_P if delta_P > 0 else 0

            gas_per_bank = net_buffer_gas / 3  # approximate equal split

            V_HP = bank_volume(gas_per_bank, P_HP, P_nozzle_min)
            V_MP = bank_volume(gas_per_bank, P_MP, P_nozzle_min)
            V_LP = bank_volume(gas_per_bank, P_LP, P_nozzle_min)

            V_total = (V_HP + V_MP + V_LP) * (1 + safety_factor / 100)

            st.subheader("📊 3-Bank Cascade Buffer Sizing")
            st.write(f"HP Bank Volume: {V_HP:.2f} m³")
            st.write(f"MP Bank Volume: {V_MP:.2f} m³")
            st.write(f"LP Bank Volume: {V_LP:.2f} m³")

        else:
            usable_pressure_diff = max(P_d, P_HP if enable_cascade else P_nozzle_min * 1.5) - P_nozzle_min
            V_total = (net_buffer_gas * P_atm / usable_pressure_diff) * (1 + safety_factor / 100)

        st.success("✅ Buffer Volume Calculation Complete")
        st.write(f"🧪 **Total Buffer Volume Required (at high pressure): {V_total:.2f} m³**")
        st.write(f"🪶 **Equivalent Volume at 1 bar: {(V_total * (P_HP - P_nozzle_min) / P_atm):.2f} m³**" if enable_cascade else "")
