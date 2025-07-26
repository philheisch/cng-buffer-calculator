import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🔁 CNG Cascade Simulation – Vehicle Refill: LP → MP → HP")

st.markdown("""
Cette simulation montre le remplissage d’un véhicule avec une séquence de banques en cascade :
- **Ordre LP → MP → HP**
- Chaque banque remplit tant que la **différence de pression avec le véhicule est suffisante**
- La pression du véhicule **augmente progressivement**
- On visualise les pressions minute par minute.
""")

# -------------------- Paramètres --------------------
P_nozzle_min = st.number_input("🔻 Target vehicle pressure (bar)", value=200.0)
delta_p_min = st.number_input("🔺 Minimum ΔP for transfer (bar)", value=5.0)

# Pression initiale des banks
P_LP = st.number_input("LP initial pressure", value=150.0)
P_MP = st.number_input("MP initial pressure", value=250.0)
P_HP = st.number_input("HP initial pressure", value=350.0)

# Volumes
V_LP = st.number_input("LP volume (m³)", value=2.0)
V_MP = st.number_input("MP volume (m³)", value=2.0)
V_HP = st.number_input("HP volume (m³)", value=2.0)
V_veh = st.number_input("Vehicle volume (m³)", value=0.3)

# Simulation
max_time = 30  # minutes
step_time = 1  # minute

if st.button("🚀 Lancer la simulation"):

    # Initialisation
    P_vehicle = 1.0  # bar (atmosphérique)
    time_series = []
    P_vehicle_series = []
    P_LP_series = []
    P_MP_series = []
    P_HP_series = []

    i = 0
    while i <= max_time and P_vehicle < P_nozzle_min:

        # Choix de la banque active selon la pression disponible
        active_bank = None
        if P_LP - P_vehicle >= delta_p_min:
            active_bank = "LP"
        elif P_MP - P_vehicle >= delta_p_min:
            active_bank = "MP"
        elif P_HP - P_vehicle >= delta_p_min:
            active_bank = "HP"
        else:
            st.warning("❌ Aucune banque n’a suffisamment de pression pour continuer le remplissage.")
            break

        # Transfert de gaz selon la banque
        transfer_volume = 0.0
        if active_bank == "LP":
            delta_P = P_LP - P_vehicle
            transfer_volume = min((delta_P / P_LP) * V_LP * 0.05, V_LP)
            P_LP -= (transfer_volume / V_LP) * P_LP
        elif active_bank == "MP":
            delta_P = P_MP - P_vehicle
            transfer_volume = min((delta_P / P_MP) * V_MP * 0.05, V_MP)
            P_MP -= (transfer_volume / V_MP) * P_MP
        elif active_bank == "HP":
            delta_P = P_HP - P_vehicle
            transfer_volume = min((delta_P / P_HP) * V_HP * 0.05, V_HP)
            P_HP -= (transfer_volume / V_HP) * P_HP

        # Mise à jour de la pression véhicule
        if transfer_volume > 0:
            P_vehicle += (transfer_volume / V_veh) * P_vehicle * 0.04
            P_vehicle = min(P_vehicle, P_nozzle_min)

        # Enregistrer les valeurs pour le graphique
        time_series.append(i)
        P_vehicle_series.append(P_vehicle)
        P_LP_series.append(P_LP)
        P_MP_series.append(P_MP)
        P_HP_series.append(P_HP)

        i += step_time

    # -------------------- Graphique --------------------
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(time_series, P_vehicle_series, label="🚐 Vehicle", color="blue")
    ax.plot(time_series, P_LP_series, label="🟧 LP bank", color="orange")
    ax.plot(time_series, P_MP_series, label="🟩 MP bank", color="green")
    ax.plot(time_series, P_HP_series, label="🟥 HP bank", color="red")
    ax.set_xlabel("Temps (min)")
    ax.set_ylabel("Pression (bar)")
    ax.set_title("📈 Évolution des pressions pendant le remplissage")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.success("✅ Simulation terminée.")
