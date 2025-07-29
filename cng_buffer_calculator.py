import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF

# Configuration de l'app
st.set_page_config(page_title="CNG Station Sizing Tool", layout="centered")
st.title("🚛 Simulateur de station GNC — Version 3.0")

# Mode simplifié ou expert
mode_expert = st.checkbox("🔧 Activer le mode expert")

st.header("🧮 Paramètres généraux")

nb_veh = st.number_input("Nombre de véhicules à remplir par heure", min_value=1, value=20)
volume_litre_1bar = st.number_input("Volume moyen du réservoir (litres à 1 bar)", min_value=1, value=300)
pression_depart = st.number_input("Pression moyenne de départ des véhicules (bar)", min_value=1, value=30)
pression_cible = st.number_input("Pression cible (bar)", min_value=100, value=230)

temperature = st.slider("🌡 Température extérieure moyenne (°C)", min_value=-10, max_value=40, value=20)
duree_fonctionnement = st.selectbox("⏱ Durée de fonctionnement de la station (heures/jour)", [8, 12, 16, 24], index=3)

# Hypothèses
debit_nozzle = 10 * 60  # 10 Nm3/min => 600 Nm3/h
debit_pompe = 800       # Nm3/h
cycle_evaporateur = 4   # heures de fonctionnement
repos_evaporateur = 1   # heure de repos

# Calculs
volume_par_vehicule = volume_litre_1bar * (pression_cible - pression_depart) / 1000
volume_total_h = volume_par_vehicule * nb_veh
nozzles_requis = int(volume_total_h / debit_nozzle + 0.999)
pompes_requises = int(volume_total_h / debit_pompe + 0.999)

# Évaporation : capacité horaire effective selon T°
efficacite_temp = 1.0 if temperature > 20 else 0.8 if temperature > 10 else 0.6
capacite_evap_horaire = debit_pompe * efficacite_temp

# Cycles d'évaporateurs
nb_cycles = duree_fonctionnement / (cycle_evaporateur + repos_evaporateur)
temps_effectif = nb_cycles * cycle_evaporateur
evap_requis = volume_total_h * duree_fonctionnement / (capacite_evap_horaire * temps_effectif)
evap_requis = int(evap_requis + 0.999)

# Répartition LP/MP/HP optimisée
buffer_15min = volume_total_h * 0.25
LP = buffer_15min * 0.5
MP = buffer_15min * 0.3
HP = buffer_15min * 0.2

# Affichage résultats
st.header("📊 Résultats")
st.write(f"Volume injecté par véhicule : **{volume_par_vehicule:.1f} Nm³**")
st.write(f"Débit total requis : **{volume_total_h:.1f} Nm³/h**")
st.write(f"Nozzles requis : **{nozzles_requis}**")
st.write(f"Pompes cryogéniques : **{pompes_requises}**")
st.write(f"Évaporateurs nécessaires : **{evap_requis}** (avec cycles {cycle_evaporateur}h / {repos_evaporateur}h)")

st.subheader("📦 Répartition optimisée des buffers")
st.write(f"Bank LP : {LP:.1f} Nm³")
st.write(f"Bank MP : {MP:.1f} Nm³")
st.write(f"Bank HP : {HP:.1f} Nm³")

# Graphique
labels = ['LP Bank', 'MP Bank', 'HP Bank']
volumes = [LP, MP, HP]
fig, ax = plt.subplots()
ax.pie(volumes, labels=labels, autopct='%1.1f%%', startangle=90)
ax.axis('equal')
st.pyplot(fig)

# Mode expert
if mode_expert:
    st.header("🧠 Options Expert (bêta)")
    st.markdown("- Réglage manuel des pressions LP/MP/HP")
    st.markdown("- (à venir) Simulation dynamique de la file d’attente")
    st.markdown("- (à venir) Visualisation pression vs. temps")

# Export PDF
def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "CNG Station Sizing Report", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.ln(5)

    pdf.cell(0, 10, f"Nombre véhicules/h : {nb_veh}", ln=True)
    pdf.cell(0, 10, f"Volume moyen véhicule : {volume_litre_1bar} L", ln=True)
    pdf.cell(0, 10, f"Pression départ : {pression_depart} bar", ln=True)
    pdf.cell(0, 10, f"Pression cible : {pression_cible} bar", ln=True)
    pdf.cell(0, 10, f"Température : {temperature} °C", ln=True)
    pdf.cell(0, 10, f"Durée fonctionnement : {duree_fonctionnement} h", ln=True)
    pdf.ln(5)

    pdf.cell(0, 10, f"Volume/veh : {volume_par_vehicule:.1f} Nm³", ln=True)
    pdf.cell(0, 10, f"Débit total : {volume_total_h:.1f} Nm³/h", ln=True)
    pdf.cell(0, 10, f"Nozzles : {nozzles_requis}", ln=True)
    pdf.cell(0, 10, f"Pompes : {pompes_requises}", ln=True)
    pdf.cell(0, 10, f"Évaporateurs : {evap_requis}", ln=True)
    pdf.ln(5)

    pdf.cell(0, 10, f"LP Bank : {LP:.1f} Nm³", ln=True)
    pdf.cell(0, 10, f"MP Bank : {MP:.1f} Nm³", ln=True)
    pdf.cell(0, 10, f"HP Bank : {HP:.1f} Nm³", ln=True)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    st.download_button("📥 Télécharger le rapport PDF", pdf_bytes, "cng_sizing_report.pdf", mime="application/pdf")

st.header("📄 Export PDF")
export_pdf()
