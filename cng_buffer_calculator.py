import streamlit as st

st.title("🔧 CNG Buffer Storage Calculator with 3-Bank Cascade")

st.header("📥 Input Parameters")

# General Inputs
Q_d = st.number_input("Downstream Flow (Nm³/h)", min_value=0.0, value=0.0, step=1.0)
P_d = st.number_input("Downstream Line Pressure (bar)", min_value=0.0, value=0.0, step=0.1)

N = st.number_input("Number of Refueling Nozzles", min_value=1, value=2, step=1)
Q_n = st.number_input("Flow per Nozzle (Nm³/min)", min_value=0.0, value=50.0, step=1.0)
t_refuel = st.number_input("Refueling Time (min)", min_value=0.0, value=10.0, step=1.0)

P_nozzle_min = st.number_input("Minimum Pressure Required at Nozzle (bar)", min_value=0.1, value=100.0, step=1.0)
safety_factor = st.number_input("Safety Margin (%)", min_value=0.0, value=10.0, step=1.0)

enable_cascade = st.checkbox("Enable 3-Bank Cascade Optimization")

if enable_cascade:
    st.subheader("3-Bank Pressures")
    P_HP = st.number_input("High Pressure Bank (HP) [bar]", min_value=float(P_nozzle_min + 1), value=250.0, step=1.0)
    P_MP = st.number_input("Mid Pressure Bank (MP) [bar]", min_value=float(P_nozzle_min + 1), value=200.0, step=1.0)
    P_LP = st.number_input("Low Pressure Bank (LP) [bar]", min_value=float(P_nozzle_min + 1), value=150.0, step=1.0)

# -------------------------------
# Perform Calculation
# -------------------------------
if st.button("🔍 Calculate Required Buffer Volume"):

    if Q_n <= 0 or N <= 0 or t_refuel <= 0:
        st.error("❌ Please enter valid positive values for nozzle flow, number, and time.")
    else:
        # Gas needs
        total_refuel_gas = N * Q_n * t_refuel  # Nm³
        Q_d_per_min = Q_d / 60.0
        downstream_contribution = 0.0

        if P_d >= P_nozzle_min:
            downstream_contribution = min(Q_d_per_min * t_refuel, total_refuel_gas)

        net_gas_needed = total_refuel_gas - downstream_contribution

        st.subheader("📊 Gas Summary")
        st.write(f"🔹 Total Gas Needed for Refueling: **{total_refuel_gas:.2f} Nm³**")
        st.write(f"🔹 Downstream Line Contribution: **{downstream_contribution:.2f} Nm³**")
        st.write(f"🔹 Net Gas Required from Buffer: **{net_gas_needed:.2f} Nm³**")

        # Pressure normalization
        P_atm = 1.013

        if enable_cascade:
            # Helper function for each bank
            def calc_bank_volume(V, P_start, P_end):
                dP = P_start - P_end
                return (V * P_atm / dP) if dP > 0 else 0.0

            gas_per_bank = net_gas_needed / 3.0

            V_HP = calc_bank_volume(gas_per_bank, P_HP, P_nozzle_min)
            V_MP = calc_bank_volume(gas_per_bank, P_MP, P_nozzle_min)
            V_LP = calc_bank_volume(gas_per_bank, P_LP, P_nozzle_min)

            total_buffer = (V_HP + V_MP + V_LP) * (1 + safety_factor / 100.0)

            st.subheader("🧱 3-Bank Cascade Volumes")
            st.write(f"HP Bank: {V_HP:.2f} m³")
            st.write(f"MP Bank: {V_MP:.2f} m³")
            st.write(f"LP Bank: {V_LP:.2f} m³")

        else:
            # Single buffer logic
            usable_delta_P = max(P_d, P_nozzle_min * 1.5) - P_nozzle_min
            total_buffer = (net_gas_needed * P_atm / usable_delta_P) * (1 + safety_factor / 100.0)

        st.success("✅ Buffer Volume Calculation Complete")
        st.write(f"📦 **Total Buffer Volume Required (at pressure): {total_buffer:.2f} m³**")
        if enable_cascade:
            st.write(f"📊 Equivalent Volume at 1 bar: {(total_buffer * (P_HP - P_nozzle_min) / P_atm):.2f} m³")
