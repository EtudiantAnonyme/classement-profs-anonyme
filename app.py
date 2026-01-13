import pandas as pd
import streamlit as st
from thefuzz import process
import matplotlib.pyplot as plt
import re

# =========================
# Chargement des données
# =========================
try:
    df = pd.read_csv("avis.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "prof","programme","cours",
        "clarte","organisation","equite","aide",
        "stress","motivation","cote_r","user_id"
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
# Programmes et cours Montmorency (complet)
# =========================
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

# =========================
# Explications utilisateurs
# =========================
st.title("Classement des professeurs – Cégep Montmorency")
st.info("""
### Comment fonctionnent les scores (1 à 10)

- **Clarté / Organisation / Équité / Aide / Motivation** → Plus c’est haut, mieux c’est.
- **Stress** → Plus c’est bas, mieux c’est (le système l’inverse automatiquement).
- **Impact sur la côte R** → Plus c’est bas, mieux c’est (le système l’inverse automatiquement).

### Profils étudiants
- **Ordinaire** : Moyenne simple, pas de pondération.
- **Cote R** : Favorise les professeurs qui améliorent la côte R.
- **Apprentissage** : Favorise la pédagogie et la motivation.
- **Chill** : Favorise l’expérience agréable et modère le stress.
- **Stress minimiser** : Favorise les professeurs qui réduisent le stress.
- **Équité focus** : Favorise les professeurs justes dans les examens.
""")

# =========================
# Validation identifiant
# =========================
def identifiant_valide(user_id: str) -> bool:
    if not user_id:
        return False
    if not re.fullmatch(r"\d{7}", user_id):
        return False
    return user_id[:2] in {"22","23","24","25","26","27"}

# =========================
# Formulaire ajout avis
# =========================
st.header("Ajouter un avis")

with st.form("avis"):
    user_id = st.text_input("Identifiant montmorency")
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
        if not identifiant_valide(user_id):
            st.error("Identifiant invalide ! Doit contenir 7 chiffres et commencer par 22-27.")
        else:
            # Anti-double vote
            already_voted = ((df["user_id"] == user_id) & (df["prof"] == prof)).any()
            if already_voted:
                st.warning("Vous avez déjà voté pour ce professeur !")
            else:
                # Fuzzy matching pour corriger faute de frappe
                def norm(x): return x.lower().strip()
                if teachers:
                    match, score = process.extractOne(norm(prof), [norm(t) for t in teachers])
                    if score >= 85:
                        prof = teachers[[norm(t) for t in teachers].index(match)]

                nouvel_avis = {
                    "prof": prof, "programme": programme, "cours": cours,
                    "clarte": clarte, "organisation": organisation, "equite": equite,
                    "aide": aide, "stress": stress, "motivation": motivation, "cote_r": cote_r,
                    "user_id": user_id
                }

                df = pd.concat([df, pd.DataFrame([nouvel_avis])], ignore_index=True)
                df.to_csv("avis.csv", index=False)
                st.success("Avis ajouté ✔")

# =========================
# Classement
# =========================
st.header("Classement des professeurs")

cours_choisi = st.selectbox("Choisir un cours", sorted(df["cours"].unique()))
profil = st.selectbox("Profil étudiant", [
    "ordinaire","cote_r","apprentissage","chill","stress_minimiser","equite_focus"
])

df_grouped = df.groupby(["prof","cours"], as_index=False)[numeric_cols].mean()
df_filtered = df_grouped[df_grouped["cours"] == cours_choisi].copy()

# Inversion des critères négatifs
df_filtered["stress_inv"] = 10 - df_filtered["stress"]
df_filtered["cote_r_inv"] = 10 - df_filtered["cote_r"]
df_filtered["pedagogie"] = df_filtered[["clarte","organisation"]].mean(axis=1)
df_filtered["experience"] = df_filtered[["stress_inv","motivation"]].mean(axis=1)

# Pondérations par profil
poids = {
    "ordinaire": None,
    "cote_r": {"pedagogie":0.25,"cote_r":0.40,"equite":0.20,"aide":0.10,"experience":0.05},
    "apprentissage": {"pedagogie":0.45,"cote_r":0.15,"equite":0.15,"aide":0.15,"experience":0.10},
    "chill": {"pedagogie":0.30,"cote_r":0.20,"equite":0.15,"aide":0.15,"experience":0.20},
    "stress_minimiser": {"pedagogie":0.25,"cote_r":0.10,"equite":0.15,"aide":0.10,"experience":0.40},
    "equite_focus": {"pedagogie":0.20,"cote_r":0.10,"equite":0.40,"aide":0.10,"experience":0.20}
}

# Calcul du score final
if profil == "ordinaire":
    df_filtered["score_final"] = df_filtered[["clarte","organisation","equite","aide","motivation","stress_inv","cote_r_inv"]].mean(axis=1)
else:
    p = poids[profil]
    df_filtered["score_final"] = (
        df_filtered["pedagogie"] * p["pedagogie"] +
        df_filtered["cote_r_inv"] * p["cote_r"] +
        df_filtered["equite"] * p["equite"] +
        df_filtered["aide"] * p["aide"] +
        df_filtered["experience"] * p["experience"]
    )

# Classement trié
df_filtered = df_filtered.sort_values("score_final", ascending=False).reset_index(drop=True)
df_filtered.index += 1

st.subheader(f"Classement – {cours_choisi} ({profil})")
st.table(df_filtered[["prof","score_final","pedagogie","equite","aide","experience","cote_r_inv"]].round(2))

# Top 3 graphique
top3 = df_filtered.head(3)
if not top3.empty:
    st.subheader("🎖 Top 3 professeurs")
    fig, ax = plt.subplots()
    ax.barh(top3["prof"], top3["score_final"], color="skyblue")
    ax.invert_yaxis()
    ax.set_xlabel("Score final")
    ax.set_title(f"Top 3 – {cours_choisi}")
    st.pyplot(fig)
