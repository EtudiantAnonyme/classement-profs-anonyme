import pandas as pd
import streamlit as st

# =========================
# Charger les avis existants
# =========================
try:
    df = pd.read_csv("avis.csv")
except FileNotFoundError:
    # créer un CSV vide si n'existe pas
    df = pd.DataFrame(columns=["prof","cours","clarte","organisation",
                               "equite","aide","stress","motivation","cote_r"])
    df.to_csv("avis.csv", index=False)

# =========================
# Ajouter un nouvel avis
# =========================
st.title("Classement des professeurs - Sciences de la nature")

st.header("Ajouter un avis")

with st.form("form_avis"):
    prof = st.text_input("Nom du professeur")
    cours = st.text_input("Cours")
    clarte = st.slider("Clarté", 1, 5, 3)
    organisation = st.slider("Organisation", 1, 5, 3)
    equite = st.slider("Équité / Examens justes", 1, 5, 3)
    aide = st.slider("Disponibilité / Aide", 1, 5, 3)
    stress = st.slider("Stress", 1, 5, 3)
    motivation = st.slider("Motivation", 1, 5, 3)
    cote_r = st.slider("Impact sur la côte R", 1, 5, 3)
    submitted = st.form_submit_button("Soumettre l'avis")

    if submitted:
        nouvel_avis = {
            "prof": prof,
            "cours": cours,
            "clarte": clarte,
            "organisation": organisation,
            "equite": equite,
            "aide": aide,
            "stress": stress,
            "motivation": motivation,
            "cote_r": cote_r
        }
        df = pd.concat([df, pd.DataFrame([nouvel_avis])], ignore_index=True)
        df.to_csv("avis.csv", index=False)
        st.success("Avis ajouté ! ✅")

# =========================
# Choisir le cours et profil pour voir le classement
# =========================
st.header("Voir le classement")

cours_choisi = st.selectbox("Choisir un cours", df["cours"].unique())
profil_etudiant = st.selectbox("Profil étudiant",
                               ["cote_r", "apprentissage", "chill"])

# =========================
# Moyenne par prof
# =========================
df_grouped = df.groupby(["prof","cours"], as_index=False).mean()

df_filtered = df_grouped[df_grouped["cours"] == cours_choisi].copy()

# Poids selon le profil
if profil_etudiant == "cote_r":
    poids = {"pedagogie":0.25, "cote_r":0.40, "equite":0.20, "aide":0.10, "experience":0.05}
elif profil_etudiant == "apprentissage":
    poids = {"pedagogie":0.45, "cote_r":0.15, "equite":0.15, "aide":0.15, "experience":0.10}
else:  # chill
    poids = {"pedagogie":0.30, "cote_r":0.20, "equite":0.15, "aide":0.15, "experience":0.20}

# Calcul des scores
df_filtered["pedagogie"] = df_filtered[["clarte","organisation"]].mean(axis=1)
df_filtered["experience"] = df_filtered[["stress","motivation"]].mean(axis=1)
df_filtered["score_final_personnalise"] = (
    df_filtered["pedagogie"] * poids["pedagogie"] +
    df_filtered["cote_r"] * poids["cote_r"] +
    df_filtered["equite"] * poids["equite"] +
    df_filtered["aide"] * poids["aide"] +
    df_filtered["experience"] * poids["experience"]
)

# Classement
classement_personnalise = df_filtered.sort_values(
    by="score_final_personnalise", ascending=False
)

st.subheader(f"Classement pour {cours_choisi} ({profil_etudiant})")
st.table(classement_personnalise[[
    "prof","cours","score_final_personnalise",
    "pedagogie","cote_r","equite","aide","experience"
]])

