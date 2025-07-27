import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

st.set_page_config(page_title="CNG Station Sizing", layout="centered")

st.title("🚛 CNG Station Auto-Sizing Tool")

st.markdown("Ce simulateur calcule automatiquement les besoins en buffers, compresseurs et nozzles à partir de quelques paramètres clés.")

st.header("🔧 Paramètres d'entrée")

# Inputs
nb_vehicules = st.number_input("Nombre de véhicules à remplir par heure", min_value=1, value=20)
volume_litre_1bar = st.number_input("Volume moyen du réservoir à 1 bar (litres)", min_value=1, value=300)
pression_depart = st.number_input("Pression moyenne de départ (bar)", min_value=1, value=30)
pression_cible = st.number_input("Pression cible (bar)", min_value=100, value=230)

# Hypothèses
debit_nozzle_max = 10 * 60  # 10 Nm3/min = 600 Nm3/h
debit_compresseur = 800     # Nm3/h
delai_compresseur = 15      # minutes sans compression

# Calculs
volume_nm3_par_vehicule = volume_litre_1bar * (pression_cible - pression_depart) / 1000
debit_total_heure = nb_vehicules * volume_nm3_par_vehicule
nozzles_requis = int((debit_total_heure / debit_nozzle_max) + 0.999)
buffer_15min = debit_total_heure * (delai_compresseur / 60)
compresseurs_requis = int((debit_total_heure / debit_compresseur) + 0.999)

# Répartition des banks (LP > MP > HP)
LP = buffer_15min * 0.5
MP = buffer_15min * 0.3
HP = buffer_15min * 0.2

# Résultats
st.header("📊 Résultats calculés")
st.write(f"Volume à injecter par véhicule : **{volume_nm3_par_vehicule:.1f} Nm³**")
st.write(f"Débit total nécessaire : **{debit_total_heure:.1f} Nm³/h**")
st.write(f"Nozzles nécessaires : **{nozzles_requis}**")
st.write(f"Compresseurs nécessaires : **{compresseurs_requis}**")
st.write(f"Buffer total pour 15 min sans compression : **{buffer_15min:.1f} Nm³**")

st.markdown("**🔋 Dimensionnement optimal des banques :**")
st.write(f"• Bank LP : {LP:.1f} Nm³")
st.write(f"• Bank MP : {MP:.1f} Nm³")
st.write(f"• Bank HP : {HP:.1f} Nm³")

# Graphique
st.header("📈 Graphique de répartition")
labels = ['LP Bank', 'MP Bank', 'HP Bank']
volumes = [LP, MP, HP]

fig, ax = plt.subplots()
ax.pie(volumes, labels=labels, autopct='%1.1f%%', startangle=90)
ax.axis('equal')
st.pyplot(fig)

# PDF export
st.header("📄 Exporter les résultats en PDF")

def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "CNG Station Sizing Report", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.ln(5)

    pdf.cell(0, 10, f"Nombre de véhicules/h : {nb_vehicules}", ln=True)
    pdf.cell(0, 10, f"Volume moyen véhicule : {volume_litre_1bar} L (1 bar)", ln=True)
    pdf.cell(0, 10, f"Pression départ : {pression_depart} bar", ln=True)
    pdf.cell(0, 10, f"Pression cible : {pression_cible} bar", ln=True)
    pdf.ln(5)

    pdf.cell(0, 10, f"Volume par véhicule : {volume_nm3_par_vehicule:.1f} Nm³", ln=True)
    pdf.cell(0, 10, f"Débit total : {debit_total_heure:.1f} Nm³/h", ln=True)
    pdf.cell(0, 10, f"Nozzles requis : {nozzles_requis}", ln=True)
    pdf.cell(0, 10, f"Compresseurs requis : {compresseurs_requis}", ln=True)
    pdf.cell(0, 10, f"Buffer 15min : {buffer_15min:.1f} Nm³", ln=True)
    pdf.ln(5)

    pdf.cell(0, 10, f"LP Bank : {LP:.1f} Nm³", ln=True)
    pdf.cell(0, 10, f"MP Bank : {MP:.1f} Nm³", ln=True)
    pdf.cell(0, 10, f"HP Bank : {HP:.1f} Nm³", ln=True)

    # Sauvegarde en mémoire
    buf = io.BytesIO()
    pdf.output(buf)
    st.download_button("📥 Télécharger le PDF", buf.getvalue(), "cng_sizing_report.pdf", mime="application/pdf")

export_pdf()
