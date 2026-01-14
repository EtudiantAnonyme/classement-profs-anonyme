import pandas as pd
import streamlit as st
from thefuzz import process
import matplotlib.pyplot as plt
import uuid

# =====================================================
# TOKEN LOCAL ANTI-SPAM (1 vote / prof / navigateur)
# =====================================================
if "user_token" not in st.session_state:
    st.session_state["user_token"] = str(uuid.uuid4())

USER_TOKEN = st.session_state["user_token"]

# =====================================================
# CHARGEMENT DES DONNÉES
# =====================================================
try:
    df = pd.read_csv("avis.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "prof", "programme", "cours",
        "clarte", "organisation", "equite", "aide",
        "stress", "motivation", "impact_note",
        "user_token"
    ])
    df.to_csv("avis.csv", index=False)

# =====================================================
# NETTOYAGE DES DONNÉES
# =====================================================
numeric_cols = [
    "clarte", "organisation", "equite", "aide",
    "stress", "motivation", "impact_note"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=numeric_cols, how="all")

teachers = sorted(df["prof"].dropna().unique().tolist())

# =====================================================
# PROGRAMMES ET COURS (Montmorency)
# =====================================================
programs = {
    "Sciences de la nature": ["Biologie","Chimie","Physique","Mathématiques","Français","Philosophie","Anglais","Éducation physique"],
    "Sciences humaines": ["Histoire","Géographie","Psychologie","Sociologie","Mathématiques","Français","Philosophie","Anglais","Éducation physique"],
    "Arts, lettres et communication": ["Français","Communication","Littérature","Anglais","Philosophie","Éducation physique"],
    "Arts visuels": ["Arts visuels","Techniques d’atelier","Histoire de l’art","Éducation physique"],
    "Danse": ["Technique de danse","Histoire de la danse","Création chorégraphique","Éducation physique"],
    "Techniques de l’informatique – Développement d’applications": ["Programmation","Bases de données","Développement Web","Mathématiques appliquées","Français","Anglais"],
    "Techniques de l’informatique – Réseaux et sécurité": ["Réseaux & sécurité","Systèmes & serveurs","Infrastructure réseau","Mathématiques appliquées","Français","Anglais"],
    "Techniques de laboratoire (multi‑disciplines)": ["Chimie analytique","Biologie appliquée","Physique de laboratoire","Mathématiques appliquées","Français"],
    "Technologie du génie civil": ["Mathématiques appliquées","Topographie","Matériaux & structures","Dessin technique","Français","Anglais"],
    "Technologie de l’architecture": ["Conception architecturale","Dessin technique","Mathématiques appliquées","Français","Anglais"],
    "Techniques de comptabilité et de gestion": ["Comptabilité","Gestion d’entreprise","Mathématiques appliquées","Français","Anglais"],
    "Techniques de services financiers et d’assurances": ["Services financiers","Risques & assurances","Mathématiques appliquées","Français","Anglais"],
    "Techniques de diététique": ["Nutrition","Sciences alimentaires","Méthodologie diététique","Français"],
    "Techniques de physiothérapie": ["Anatomie","Physiothérapie appliquée","Biologie humaine","Français"],
    "Techniques de sécurité incendie": ["Sécurité incendie","Prévention des risques","Mathématiques appliquées","Français"],
    "Techniques d’intégration multimédia": ["Multimédia","Web & design","Programmation multimédia","Français","Anglais"],
    "Paysage et commercialisation en horticulture ornementale": ["Horticulture","Paysage","Gestion en horticulture","Français"],
    "Muséologie": ["Documentation de collections","Conservation","Exposition","Français"],
    "Soins infirmiers": ["Sciences infirmières","Anatomie & physiologie","Soins cliniques","Français"],
    "Physiothérapie": ["Anatomie","Physiothérapie appliquée","Biologie","Français"],
    "Génie civil": ["Mathématiques appliquées","Topographie","Matériaux & structures","Dessin technique","Français","Anglais"],
    "Génie mécanique": ["Mathématiques appliquées","Physique","Mécanique","Dessin technique","Français","Anglais"],
    "Génie informatique": ["Programmation","Algorithmique","Systèmes & réseaux","Mathématiques appliquées","Français","Anglais"]
}

# =====================================================
# TITRE ET EXPLICATIONS
# =====================================================
st.title("Classement des professeurs – Cégep Montmorency")

st.info("""
### Comment sont calculés les scores (échelle de 1 à 10)

- **Clarté** : Le professeur explique clairement la matière et rend les concepts compréhensibles.  
- **Organisation** : Le cours est bien structuré (planification, évaluations, rythme).  
- **Équité** : Les évaluations sont justes et cohérentes pour tous les étudiants.  
- **Aide** : Le professeur est disponible et soutient les étudiants.  
- **Motivation** : Le professeur rend le cours intéressant et engageant.  
- **Stress** : Niveau de pression ressenti (plus bas = mieux).  
- **Impact académique (note / Z‑score)** : Effet perçu du professeur sur la performance de l’étudiant.

### Profils étudiants
- **Ordinaire** : Moyenne simple de tous les critères.  
- **Cote R** : Favorise l’impact académique positif.  
- **Apprentissage** : Accent sur pédagogie et motivation.  
- **Chill** : Expérience agréable avec moins de stress.  
- **Stress minimiser** : Priorité à la réduction du stress.  
- **Équité focus** : Accent sur la justice des évaluations.
""")

# =====================================================
# FORMULAIRE D’AJOUT D’AVIS
# =====================================================
st.header("Ajouter un avis")

with st.form("formulaire_avis"):

    prof_existant = st.selectbox(
        "Professeur existant",
        [""] + teachers
    )

    prof_nouveau = st.text_input(
        "Ou ajouter un nouveau professeur"
    )

    prof = prof_nouveau.strip() if prof_nouveau.strip() else prof_existant

    programme = st.selectbox(
        "Programme",
        list(programs.keys())
    )

    # ✅ BUG CORRIGÉ : cours dépend bien du programme choisi
    cours = st.selectbox(
        "Cours",
        programs[programme]
    )

    clarte = st.slider("Clarté", 1, 10, 5)
    organisation = st.slider("Organisation", 1, 10, 5)
    equite = st.slider("Équité", 1, 10, 5)
    aide = st.slider("Aide", 1, 10, 5)
    stress = st.slider("Stress (bas = mieux)", 1, 10, 5)
    motivation = st.slider("Motivation", 1, 10, 5)
    impact_note = st.slider("Impact académique (bas = mieux)", 1, 10, 5)

    envoyer = st.form_submit_button("Soumettre l’avis")

    if envoyer and prof:

        # ANTI-SPAM : 1 vote par professeur par navigateur
        deja_vote = (
            (df["user_token"] == USER_TOKEN) &
            (df["prof"] == prof)
        ).any()

        if deja_vote:
            st.warning("Vous avez déjà évalué ce professeur.")
        else:
            # Correction automatique des fautes de frappe
            def norm(x): return x.lower().strip()

            if teachers:
                match, score = process.extractOne(
                    norm(prof),
                    [norm(t) for t in teachers]
                )
                if score >= 85:
                    prof = teachers[
                        [norm(t) for t in teachers].index(match)
                    ]

            nouvel_avis = {
                "prof": prof,
                "programme": programme,
                "cours": cours,
                "clarte": clarte,
                "organisation": organisation,
                "equite": equite,
                "aide": aide,
                "stress": stress,
                "motivation": motivation,
                "impact_note": impact_note,
                "user_token": USER_TOKEN
            }

            df = pd.concat(
                [df, pd.DataFrame([nouvel_avis])],
                ignore_index=True
            )

            df.to_csv("avis.csv", index=False)
            st.success("Avis ajouté avec succès ✔")

# =====================================================
# CLASSEMENT DES PROFESSEURS
# =====================================================
st.header("Classement des professeurs")

if df.empty:
    st.info("Aucun avis disponible pour le moment.")
    st.stop()

cours_choisi = st.selectbox(
    "Choisir un cours",
    sorted(df["cours"].unique())
)

profil = st.selectbox(
    "Profil étudiant",
    [
        "ordinaire",
        "cote_r",
        "apprentissage",
        "chill",
        "stress_minimiser",
        "equite_focus"
    ]
)

df_grouped = df.groupby(
    ["prof", "cours"],
    as_index=False
)[numeric_cols].mean()

df_filtered = df_grouped[
    df_grouped["cours"] == cours_choisi
].copy()

# Inversion des critères négatifs
df_filtered["stress_inv"] = 10 - df_filtered["stress"]
df_filtered["impact_inv"] = 10 - df_filtered["impact_note"]

df_filtered["pedagogie"] = df_filtered[
    ["clarte", "organisation"]
].mean(axis=1)

df_filtered["experience"] = df_filtered[
    ["stress_inv", "motivation"]
].mean(axis=1)

# Pondérations
poids = {
    "ordinaire": None,
    "cote_r": {
        "pedagogie": 0.25,
        "impact": 0.40,
        "equite": 0.20,
        "aide": 0.10,
        "experience": 0.05
    },
    "apprentissage": {
        "pedagogie": 0.45,
        "impact": 0.15,
        "equite": 0.15,
        "aide": 0.15,
        "experience": 0.10
    },
    "chill": {
        "pedagogie": 0.30,
        "impact": 0.20,
        "equite": 0.15,
        "aide": 0.15,
        "experience": 0.20
    },
    "stress_minimiser": {
        "pedagogie": 0.25,
        "impact": 0.10,
        "equite": 0.15,
        "aide": 0.10,
        "experience": 0.40
    },
    "equite_focus": {
        "pedagogie": 0.20,
        "impact": 0.10,
        "equite": 0.40,
        "aide": 0.10,
        "experience": 0.20
    }
}

# Calcul score final
if profil == "ordinaire":
    df_filtered["score_final"] = df_filtered[
        ["clarte", "organisation", "equite", "aide",
         "motivation", "stress_inv", "impact_inv"]
    ].mean(axis=1)
else:
    p = poids[profil]
    df_filtered["score_final"] = (
        df_filtered["pedagogie"] * p["pedagogie"]
        + df_filtered["impact_inv"] * p["impact"]
        + df_filtered["equite"] * p["equite"]
        + df_filtered["aide"] * p["aide"]
        + df_filtered["experience"] * p["experience"]
    )

df_filtered = df_filtered.sort_values(
    "score_final",
    ascending=False
).reset_index(drop=True)

df_filtered.index += 1

st.subheader(f"Classement – {cours_choisi}")
st.table(
    df_filtered[["prof", "score_final"]].round(2)
)

# =====================================================
# TOP 3 – GRAPHIQUE
# =====================================================
top3 = df_filtered.head(3)

if not top3.empty:
    st.subheader("🏆 Top 3 professeurs")
    fig, ax = plt.subplots()
    ax.barh(top3["prof"], top3["score_final"])
    ax.invert_yaxis()
    ax.set_xlabel("Score final")
    st.pyplot(fig)
