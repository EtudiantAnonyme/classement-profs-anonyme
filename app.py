import pandas as pd
import streamlit as st
from thefuzz import process

# =========================
# Charger les avis existants
# =========================
try:
    df = pd.read_csv("avis.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "prof", "programme", "cours",
        "clarte", "organisation", "equite",
        "aide", "stress", "motivation", "cote_r"
    ])
    df.to_csv("avis.csv", index=False)

# =========================
# Nettoyage des données
# =========================
numeric_cols = ["clarte", "organisation", "equite", "aide", "stress", "motivation", "cote_r"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=numeric_cols, how="all")

teachers = df["prof"].dropna().unique().tolist()

# =========================
# Programmes (catégories réalistes)
# =========================
programs = {
    "Sciences de la nature": ["Biologie", "Chimie", "Physique", "Mathématiques", "Français", "Philosophie", "Anglais", "Éducation physique"],
    "Sciences humaines": ["Histoire", "Géographie", "Psychologie", "Sociologie", "Mathématiques", "Français", "Philosophie", "Anglais", "Éducation physique"],
    "Techniques de l’informatique": ["Programmation", "Algorithmique", "Réseaux", "Bases de données", "Mathématiques appliquées", "Français", "Anglais"],
    "Génie civil": ["Mathématiques appliquées", "Topographie", "Structures", "Dessin technique", "Physique", "Français", "Anglais"],
    "Génie mécanique": ["Mathématiques appliquées", "Mécanique", "Physique", "Dessin technique", "Français", "Anglais"],
    "Soins infirmiers": ["Soins cliniques", "Anatomie", "Physiologie", "Biologie", "Français"],
    "Techniques de laboratoire": ["Chimie", "Biologie", "Physique", "Mathématiques appliquées", "Français"],
    "Techniques de comptabilité": ["Comptabilité", "Gestion", "Mathématiques appliquées", "Français", "Anglais"]
}

# =========================
# Titre et explications
# =========================
st.title("Classement anonyme des professeurs – Cégep Montmorency")

st.info("""
### Comment fonctionnent les notes (1 à 10)

- **Clarté** : qualité des explications  
- **Organisation** : structure et préparation  
- **Équité** : justice des évaluations  
- **Aide** : disponibilité du professeur  
- **Stress** : plus c’est bas, mieux c’est  
- **Motivation** : donne envie de s’impliquer  
- **Impact sur la cote R** : plus c’est bas, moins ça nuit à ta cote R  

👉 **Profil ordinaire** = moyenne simple sur 10  
👉 **Autres profils** = pondérations différentes selon l’objectif
""")

# =========================
# Formulaire d'avis
# =========================
st.header("Ajouter un avis")

with st.form("form_avis"):
    prof_existant = st.selectbox("Professeur existant (facultatif)", [""] + teachers)
    prof_libre = st.text_input("Ou écrire le nom du professeur")

    prof = prof_libre.strip() if prof_libre else prof_existant.strip()

    programme = st.selectbox("Programme", list(programs.keys()))
    cours = st.selectbox("Catégorie de cours", programs[programme])

    clarte = st.slider("Clarté", 1, 10, 5)
    organisation = st.slider("Organisation", 1, 10, 5)
    equite = st.slider("Équité", 1, 10, 5)
    aide = st.slider("Aide", 1, 10, 5)
    stress = st.slider("Stress", 1, 10, 5)
    motivation = st.slider("Motivation", 1, 10, 5)
    cote_r = st.slider("Impact sur la cote R", 1, 10, 5)

    submitted = st.form_submit_button("Soumettre")

    if submitted and prof:
        def norm(s): return s.lower().strip()

        if teachers:
            match, score = process.extractOne(norm(prof), [norm(t) for t in teachers])
            if score >= 80:
                prof = teachers[[norm(t) for t in teachers].index(match)]

        new_row = {
            "prof": prof,
            "programme": programme,
            "cours": cours,
            "clarte": clarte,
            "organisation": organisation,
            "equite": equite,
            "aide": aide,
            "stress": stress,
            "motivation": motivation,
            "cote_r": cote_r
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv("avis.csv", index=False)

        st.success("Avis ajouté avec succès ✅")

# =========================
# Classement
# =========================
st.header("Voir le classement")

if df.empty:
    st.warning("Aucun avis disponible.")
else:
    cours_choisi = st.selectbox("Choisir une catégorie", sorted(df["cours"].unique()))

    profil = st.selectbox(
        "Profil étudiant",
        ["ordinaire", "cote_r", "apprentissage", "chill", "stress_minimiser", "equite_focus"]
    )

    df_grouped = df.groupby(["prof", "cours"], as_index=False)[numeric_cols].mean()
    df_filtered = df_grouped[df_grouped["cours"] == cours_choisi].copy()

    df_filtered["pedagogie"] = df_filtered[["clarte", "organisation"]].mean(axis=1)
    df_filtered["experience"] = df_filtered[["stress", "motivation"]].mean(axis=1)

    poids_profiles = {
        "cote_r": {"pedagogie":0.25, "cote_r":0.40, "equite":0.20, "aide":0.10, "experience":0.05},
        "apprentissage": {"pedagogie":0.45, "cote_r":0.15, "equite":0.15, "aide":0.15, "experience":0.10},
        "chill": {"pedagogie":0.30, "cote_r":0.20, "equite":0.15, "aide":0.15, "experience":0.20},
        "stress_minimiser": {"pedagogie":0.25, "cote_r":0.10, "equite":0.15, "aide":0.10, "experience":0.40},
        "equite_focus": {"pedagogie":0.20, "cote_r":0.10, "equite":0.40, "aide":0.10, "experience":0.20}
    }

    if profil == "ordinaire":
        df_filtered["score"] = df_filtered[
            ["pedagogie", "cote_r", "equite", "aide", "experience"]
        ].mean(axis=1)
    else:
        p = poids_profiles[profil]
        df_filtered["score"] = (
            df_filtered["pedagogie"] * p["pedagogie"] +
            df_filtered["cote_r"] * p["cote_r"] +
            df_filtered["equite"] * p["equite"] +
            df_filtered["aide"] * p["aide"] +
            df_filtered["experience"] * p["experience"]
        )

    df_filtered = df_filtered.sort_values("score", ascending=False)

    st.subheader(f"Classement – {cours_choisi} ({profil})")
    st.dataframe(
        df_filtered[["prof", "score", "pedagogie", "cote_r", "equite", "aide", "experience"]]
        .round(2),
        use_container_width=True
    )
