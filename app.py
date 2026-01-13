import pandas as pd
import streamlit as st
from thefuzz import process

# =========================
# Chargement des données
# =========================
try:
    df = pd.read_csv("avis.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "prof","programme","cours",
        "clarte","organisation","equite",
        "aide","stress","motivation","cote_r"
    ])
    df.to_csv("avis.csv", index=False)

# =========================
# Nettoyage
# =========================
numeric_cols = ["clarte","organisation","equite","aide","stress","motivation","cote_r"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=numeric_cols, how="all")

teachers = sorted(df["prof"].dropna().unique().tolist())

# =========================
# Programmes (Montmorency)
# =========================
programs = {
    "Sciences de la nature": ["Biologie","Chimie","Physique","Mathématiques","Français","Philosophie","Éducation physique"],
    "Sciences humaines": ["Histoire","Géographie","Psychologie","Sociologie","Mathématiques","Français","Philosophie","Éducation physique"],
    "Techniques de l’informatique": ["Programmation","Bases de données","Réseaux","Mathématiques appliquées","Français"],
    "Génie": ["Mathématiques appliquées","Physique","Mécanique","Programmation","Français"],
    "Soins infirmiers": ["Sciences infirmières","Anatomie","Soins cliniques","Français"]
}

# =========================
# Interface – explication
# =========================
st.title("Classement des professeurs – Cégep Montmorency")

st.info("""
### Comment fonctionnent les scores (1 à 10)

• **Clarté / Organisation / Équité / Aide / Motivation**  
→ Plus c’est haut, mieux c’est.

• **Stress**  
→ Plus c’est bas, mieux c’est (le système l’inverse automatiquement).

• **Impact sur la cote R**  
→ Plus c’est bas, mieux c’est (le système l’inverse automatiquement).

👉 Tous les classements finaux sont sur **10**.
""")

# =========================
# Ajouter un avis
# =========================
st.header("Ajouter un avis")

with st.form("avis"):
    prof_existant = st.selectbox("Professeur existant", [""] + teachers)
    prof_nouveau = st.text_input("Ou nouveau professeur")

    prof = prof_nouveau.strip() if prof_nouveau.strip() else prof_existant

    programme = st.selectbox("Programme", list(programs.keys()))
    cours = st.selectbox("Cours", programs[programme])

    clarte = st.slider("Clarté", 1, 10, 5)
    organisation = st.slider("Organisation", 1, 10, 5)
    equite = st.slider("Équité", 1, 10, 5)
    aide = st.slider("Aide", 1, 10, 5)
    stress = st.slider("Stress (bas = mieux)", 1, 10, 5)
    motivation = st.slider("Motivation", 1, 10, 5)
    cote_r = st.slider("Impact sur la cote R (bas = mieux)", 1, 10, 5)

    envoyer = st.form_submit_button("Soumettre")

    if envoyer and prof:
        def norm(x): return x.lower().strip()

        if teachers:
            match, score = process.extractOne(norm(prof), [norm(t) for t in teachers])
            if score >= 85:
                prof = teachers[[norm(t) for t in teachers].index(match)]

        df = pd.concat([df, pd.DataFrame([{
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
        }])], ignore_index=True)

        df.to_csv("avis.csv", index=False)
        st.success("Avis ajouté ✔")

# =========================
# Classement
# =========================
st.header("Classement des professeurs")

cours_choisi = st.selectbox("Choisir un cours", sorted(df["cours"].unique()))

profil = st.selectbox("Profil étudiant", [
    "ordinaire",
    "cote_r",
    "apprentissage",
    "chill",
    "stress_minimiser",
    "equite_focus"
])

# =========================
# Moyennes
# =========================
df_grouped = df.groupby(["prof","cours"], as_index=False)[numeric_cols].mean()
df = df_grouped[df_grouped["cours"] == cours_choisi].copy()

# Inversion des critères négatifs
df["stress_inv"] = 10 - df["stress"]
df["cote_r_inv"] = 10 - df["cote_r"]

df["pedagogie"] = df[["clarte","organisation"]].mean(axis=1)
df["experience"] = df[["stress_inv","motivation"]].mean(axis=1)

# =========================
# Profils
# =========================
poids = {
    "ordinaire": None,  # moyenne simple
    "cote_r": {"pedagogie":0.25,"cote_r":0.40,"equite":0.20,"aide":0.10,"experience":0.05},
    "apprentissage": {"pedagogie":0.45,"cote_r":0.15,"equite":0.15,"aide":0.15,"experience":0.10},
    "chill": {"pedagogie":0.30,"cote_r":0.20,"equite":0.15,"aide":0.15,"experience":0.20},
    "stress_minimiser": {"pedagogie":0.25,"cote_r":0.10,"equite":0.15,"aide":0.10,"experience":0.40},
    "equite_focus": {"pedagogie":0.20,"cote_r":0.10,"equite":0.40,"aide":0.10,"experience":0.20}
}

# =========================
# Score final
# =========================
if profil == "ordinaire":
    df["score_final"] = df[
        ["clarte","organisation","equite","aide","motivation","stress_inv","cote_r_inv"]
    ].mean(axis=1)
else:
    p = poids[profil]
    df["score_final"] = (
        df["pedagogie"] * p["pedagogie"] +
        df["cote_r_inv"] * p["cote_r"] +
        df["equite"] * p["equite"] +
        df["aide"] * p["aide"] +
        df["experience"] * p["experience"]
    )

# =========================
# Classement final
# =========================
df = df.sort_values("score_final", ascending=False).reset_index(drop=True)
df.index += 1

st.subheader(f"Classement – {cours_choisi} ({profil})")

st.table(df[[
    "prof","score_final","pedagogie","equite","aide","experience","cote_r_inv"
]].round(2))
