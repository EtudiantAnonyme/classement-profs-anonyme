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
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna(subset=numeric_cols, how='all')

# =========================
# Liste dynamique des professeurs
# =========================
teachers = df["prof"].unique().tolist()

# =========================
# Programmes et cours (Montmorency)
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
# Explications pour les utilisateurs
# =========================
st.title("Classement des professeurs - Cégep Montmorency")
st.info("""
**Comment noter les professeurs :**

- **Clarté (1-10)** : Comment le professeur explique le cours.
- **Organisation (1-10)** : Préparation et structure du cours.
- **Équité (1-10)** : Examens et évaluations justes.
- **Aide (1-10)** : Disponibilité du professeur pour répondre aux questions.
- **Stress (1-10)** : Plus c’est bas, mieux vous vous sentez dans le cours.
- **Motivation (1-10)** : Le professeur vous motive à apprendre.
- **Impact sur la côte R (1-10)** : Plus c’est bas, moins le cours impacte négativement votre R score.
""")

# =========================
# Formulaire d'avis
# =========================
st.header("Ajouter un avis")
with st.form("form_avis"):
    st.write("Choisissez un professeur existant ou tapez un nouveau :")
    
    selected_teacher = st.selectbox("Professeur existant :", options=teachers, index=0 if teachers else None)
    typed_teacher = st.text_input("Ou tapez un nouveau professeur :")
    user_prof = typed_teacher if typed_teacher else selected_teacher
    
    program = st.selectbox("Choisissez votre programme", list(programs.keys()))
    cours = st.selectbox("Choisissez une catégorie", programs[program])
    
    clarte = st.slider("Clarté", 1, 10, 5)
    organisation = st.slider("Organisation", 1, 10, 5)
    equite = st.slider("Équité / Examens justes", 1, 10, 5)
    aide = st.slider("Disponibilité / Aide", 1, 10, 5)
    stress = st.slider("Stress", 1, 10, 5)
    motivation = st.slider("Motivation", 1, 10, 5)
    cote_r = st.slider("Impact sur la côte R", 1, 10, 5)
    
    submitted = st.form_submit_button("Soumettre l'avis")
    
    if submitted and user_prof:
        def normalize(s): return s.strip().lower()
        if teachers:
            best_match, score = process.extractOne(normalize(user_prof), [normalize(t) for t in teachers])
        else: score = 0
        
        if score >= 80:
            matched_prof = teachers[[normalize(t) for t in teachers].index(best_match)]
            st.info(f"Nom du professeur reconnu : {matched_prof}")
        else:
            matched_prof = user_prof
            if matched_prof not in teachers: teachers.append(matched_prof)
        
        nouvel_avis = {
            "prof": matched_prof, "programme": program, "cours": cours,
            "clarte": clarte, "organisation": organisation, "equite": equite,
            "aide": aide, "stress": stress, "motivation": motivation, "cote_r": cote_r
        }
        df = pd.concat([df, pd.DataFrame([nouvel_avis])], ignore_index=True)
        df.to_csv("avis.csv", index=False)
        st.success(f"Avis ajouté pour {matched_prof} ✅")

# =========================
# Classement
# =========================
st.header("Voir le classement")

# Choix du cours
cours_choisi = st.selectbox("Choisir le cours", sorted(df["cours"].unique()))

# Choix du profil étudiant (avec le profil ordinaire ajouté)
profil_etudiant = st.selectbox(
    "Profil étudiant",
    ["cote_r","apprentissage","chill","stress_minimiser","equite_focus","ordinaire"]
)

# S'assurer que toutes les colonnes numériques sont bien au format numérique
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Moyenne par prof pour chaque cours
df_grouped = df.groupby(["prof","cours"], as_index=False)[numeric_cols].mean()
df_filtered = df_grouped[df_grouped["cours"] == cours_choisi].copy()

# Définition des pondérations selon le profil
poids_profiles = {
    "cote_r": {"pedagogie":0.25, "cote_r":0.40, "equite":0.20, "aide":0.10, "experience":0.05},
    "apprentissage": {"pedagogie":0.45, "cote_r":0.15, "equite":0.15, "aide":0.15, "experience":0.10},
    "chill": {"pedagogie":0.30, "cote_r":0.20, "equite":0.15, "aide":0.15, "experience":0.20},
    "stress_minimiser": {"pedagogie":0.25, "cote_r":0.10, "equite":0.15, "aide":0.10, "experience":0.40},
    "equite_focus": {"pedagogie":0.20, "cote_r":0.10, "equite":0.40, "aide":0.10, "experience":0.20},
    "ordinaire": {"pedagogie":1, "cote_r":1, "equite":1, "aide":1, "experience":1}  # tous égaux
}

# Récupérer les poids pour le profil choisi
poids = poids_profiles.get(profil_etudiant, poids_profiles["cote_r"])

# Calcul des scores
df_filtered["pedagogie"] = df_filtered[["clarte","organisation"]].mean(axis=1)
df_filtered["experience"] = df_filtered[["stress","motivation"]].mean(axis=1)
df_filtered["score_final_personnalise"] = (
    df_filtered["pedagogie"]*poids["pedagogie"] +
    df_filtered["cote_r"]*poids["cote_r"] +
    df_filtered["equite"]*poids["equite"] +
    df_filtered["aide"]*poids["aide"] +
    df_filtered["experience"]*poids["experience"]
)

# Classement final
classement_personnalise = df_filtered.sort_values(by="score_final_personnalise", ascending=False)

# Affichage
st.subheader(f"Classement pour {cours_choisi} ({profil_etudiant})")
st.table(classement_personnalise[[
    "prof","cours","score_final_personnalise","pedagogie","cote_r","equite","aide","experience"
]])
