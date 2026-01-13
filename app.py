import pandas as pd
import streamlit as st
from thefuzz import process

# =========================
# Charger les avis existants
# =========================
try:
    df = pd.read_csv("avis.csv")
except FileNotFoundError:
    # Créer un CSV vide si n'existe pas
    df = pd.DataFrame(columns=[
        "prof","programme","cours",
        "clarte","organisation","equite","aide","stress","motivation","cote_r"
    ])
    df.to_csv("avis.csv", index=False)

# =========================
# Convertir les colonnes numériques et nettoyer
# =========================
numeric_cols = ["clarte","organisation","equite","aide","stress","motivation","cote_r"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')  # transforme les erreurs en NaN
df = df.dropna(subset=numeric_cols, how='all')  # enlève les lignes totalement invalides

# =========================
# Liste dynamique des professeurs
# =========================
teachers = df["prof"].unique().tolist()

# =========================
# Liste des programmes et catégories de cours (Montmorency réaliste)
# =========================
programs = {
    "Sciences de la nature": ["Biologie", "Chimie", "Physique", "Mathématiques", "Français", "Philosophie", "Anglais", "Éducation physique"],
    "Sciences humaines": ["Histoire", "Géographie", "Psychologie", "Sociologie", "Mathématiques", "Français", "Philosophie", "Anglais", "Éducation physique"],
    "Arts, lettres et communication": ["Français", "Communication", "Littérature", "Anglais", "Philosophie", "Éducation physique"],
    "Arts visuels": ["Arts visuels", "Techniques d’atelier", "Histoire de l’art", "Éducation physique"],
    "Danse": ["Technique de danse", "Histoire de la danse", "Création chorégraphique", "Éducation physique"],

    "Techniques de l’informatique – Développement d’applications": ["Programmation", "Bases de données", "Développement Web", "Mathématiques appliquées", "Français", "Anglais"],
    "Techniques de l’informatique – Réseaux et sécurité": ["Réseaux & sécurité", "Systèmes & serveurs", "Infrastructure réseau", "Mathématiques appliquées", "Français", "Anglais"],
    "Techniques de laboratoire (multi‑disciplines)": ["Chimie analytique", "Biologie appliquée", "Physique de laboratoire", "Mathématiques appliquées", "Français"],
    "Technologie du génie civil": ["Mathématiques appliquées", "Topographie", "Matériaux & structures", "Dessin technique", "Français", "Anglais"],
    "Technologie de l’architecture": ["Conception architecturale", "Dessin technique", "Mathématiques appliquées", "Français", "Anglais"],
    "Techniques de comptabilité et de gestion": ["Comptabilité", "Gestion d’entreprise", "Mathématiques appliquées", "Français", "Anglais"],
    "Techniques de services financiers et d’assurances": ["Services financiers", "Risques & assurances", "Mathématiques appliquées", "Français", "Anglais"],
    "Techniques de diététique": ["Nutrition", "Sciences alimentaires", "Méthodologie diététique", "Français"],
    "Techniques de physiothérapie": ["Anatomie", "Physiothérapie appliquée", "Biologie humaine", "Français"],
    "Techniques de sécurité incendie": ["Sécurité incendie", "Prévention des risques", "Mathématiques appliquées", "Français"],
    "Techniques d’intégration multimédia": ["Multimédia", "Web & design", "Programmation multimédia", "Français", "Anglais"],
    "Paysage et commercialisation en horticulture ornementale": ["Horticulture", "Paysage", "Gestion en horticulture", "Français"],
    "Muséologie": ["Documentation de collections", "Conservation", "Exposition", "Français"],
    "Soins infirmiers": ["Sciences infirmières", "Anatomie & physiologie", "Soins cliniques", "Français"],
    "Physiothérapie": ["Anatomie", "Physiothérapie appliquée", "Biologie", "Français"],
    "Génie civil": ["Mathématiques appliquées", "Topographie", "Matériaux & structures", "Dessin technique", "Français", "Anglais"],
    "Génie mécanique": ["Mathématiques appliquées", "Physique", "Mécanique", "Dessin technique", "Français", "Anglais"],
    "Génie informatique": ["Programmation", "Algorithmique", "Systèmes & réseaux", "Mathématiques appliquées", "Français", "Anglais"]
}

# =========================
# Ajouter un nouvel avis
# =========================
st.title("Classement des professeurs - Cégep Montmorency")
st.header("Ajouter un avis")

with st.form("form_avis"):
    st.write("Choisissez un professeur existant ou tapez un nouveau :")
    
    # Dropdown des professeurs existants
    selected_teacher = st.selectbox(
        "Professeur existant :", options=teachers, index=0 if teachers else None
    )
    
    # Entrée texte pour un nouveau professeur
    typed_teacher = st.text_input("Ou tapez un nouveau professeur :")
    
    # Déterminer le nom final
    user_prof = typed_teacher if typed_teacher else selected_teacher
    
    # Sélection du programme
    program = st.selectbox("Choisissez votre programme", list(programs.keys()))
    
    # Sélection du cours selon le programme
    cours = st.selectbox("Choisissez une catégorie", programs[program])
    
    # Sliders
    clarte = st.slider("Clarté", 1, 5, 3)
    organisation = st.slider("Organisation", 1, 5, 3)
    equite = st.slider("Équité / Examens justes", 1, 5, 3)
    aide = st.slider("Disponibilité / Aide", 1, 5, 3)
    stress = st.slider("Stress", 1, 5, 3)
    motivation = st.slider("Motivation", 1, 5, 3)
    cote_r = st.slider("Impact sur la côte R", 1, 5, 3)
    
    submitted = st.form_submit_button("Soumettre l'avis")
    
    if submitted and user_prof:
        # Fuzzy matching pour corriger les typos
        def normalize(s):
            return s.strip().lower()
        
        if teachers:
            best_match, score = process.extractOne(
                normalize(user_prof),
                [normalize(t) for t in teachers]
            )
        else:
            score = 0
        
        if score >= 80:
            matched_prof = teachers[[normalize(t) for t in teachers].index(best_match)]
            st.info(f"Nom du professeur reconnu : {matched_prof}")
        else:
            matched_prof = user_prof
            if matched_prof not in teachers:
                teachers.append(matched_prof)
                st.info(f"Nouvel enseignant ajouté : {matched_prof}")
        
        # Sauvegarder l'avis
        nouvel_avis = {
            "prof": matched_prof,
            "programme": program,
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
        st.success(f"Avis ajouté pour {matched_prof} ✅")

# =========================
# Voir le classement
# =========================
st.header("Voir le classement")

cours_choisi = st.selectbox(
    "Choisir le cours",
    sorted(df["cours"].unique())
)

profil_etudiant = st.selectbox(
    "Profil étudiant",
    ["cote_r", "apprentissage", "chill"]
)

# Moyenne par prof (en s'assurant que numeric_cols sont bien numériques)
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df_grouped = df.groupby(["prof","cours"], as_index=False)[numeric_cols].mean()
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
