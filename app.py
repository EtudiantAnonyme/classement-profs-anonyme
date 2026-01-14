import pandas as pd
import streamlit as st
from thefuzz import process
import matplotlib.pyplot as plt
import uuid
from supabase import create_client, Client

# =====================================================
# CONFIGURATION SUPABASE
# =====================================================
SUPABASE_URL = "https://lrwblhccggtctaqlrccg.supabase.co"
SUPABASE_KEY = "sb_publishable_5WzWNEn7jiF2ewvSfkK7vQ_t-nUvR4t"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =====================================================
# TOKEN LOCAL ANTI-SPAM
# =====================================================
if "user_token" not in st.session_state:
    st.session_state["user_token"] = str(uuid.uuid4())
USER_TOKEN = st.session_state["user_token"]

# =====================================================
# CHARGEMENT DES DONNÉES
# =====================================================
data = supabase.table("avis").select("*").execute()
df = pd.DataFrame(data.data) if data.data else pd.DataFrame()

# Nettoyage
numeric_cols = ["clarte","organisation","equite","aide","stress","motivation","impact_note"]
if not df.empty:
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=numeric_cols, how="all")
teachers = sorted(df["prof"].dropna().unique().tolist()) if not df.empty else []

# =====================================================
# PROGRAMMES ET COURS (inchangé)
# =====================================================
programs = { 
    "Sciences de la nature": ["Biologie","Chimie","Physique","Mathématiques","Français","Philosophie","Anglais","Éducation physique"],
    "Sciences humaines": ["Histoire","Géographie","Psychologie","Sociologie","Mathématiques","Français","Philosophie","Anglais","Éducation physique"],
    "Arts, lettres et communication": ["Français","Communication","Littérature","Anglais","Philosophie","Éducation physique"],
    # ... garder tous les autres programmes comme avant ...
}

# =====================================================
# TITRE ET INFO
# =====================================================
st.title("Classement des professeurs – Cégep Montmorency")
st.info("""
### Calcul des scores (0 à 10)

Chaque critère mesure un aspect de l’enseignement ou du cours :  

- **Clarté**, **Organisation**, **Équité**, **Aide**, **Motivation**, **Stress**, **Impact académique**
""")

# =====================================================
# FORMULAIRE D’AVIS
# =====================================================
st.header("Ajouter un avis")

prof_existant = st.selectbox("Professeur existant", [""] + teachers)
prof_nouveau = st.text_input("Ou ajouter un nouveau professeur")
prof = prof_nouveau.strip() if prof_nouveau.strip() else prof_existant

programme = st.selectbox("Programme", list(programs.keys()))
cours = st.selectbox("Cours", programs[programme])

with st.form("formulaire_avis"):
    clarte = st.slider("Clarté", 0, 10, 5)
    organisation = st.slider("Organisation", 0, 10, 5)
    equite = st.slider("Équité", 0, 10, 5)
    aide = st.slider("Aide", 0, 10, 5)
    stress = st.slider("Stress (bas = mieux)", 0, 10, 5)
    motivation = st.slider("Motivation", 0, 10, 5)
    impact_note = st.slider("Impact académique (bas = mieux)", 0, 10, 5)

    envoyer = st.form_submit_button("Soumettre l’avis")

    if envoyer and prof:
        deja_vote = ((df["user_token"] == USER_TOKEN) & (df["prof"] == prof)).any() if not df.empty else False
        if deja_vote:
            st.warning("Vous avez déjà évalué ce professeur.")
        else:
            # Normalisation
            def norm(x): return x.lower().strip()
            if teachers:
                match, score = process.extractOne(norm(prof), [norm(t) for t in teachers])
                if score >= 85:
                    prof = teachers[[norm(t) for t in teachers].index(match)]

            # Insertion Supabase
            supabase.table("avis").insert({
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
            }).execute()
            st.success("Avis ajouté avec succès ✔")

            # Reload data
            data = supabase.table("avis").select("*").execute()
            df = pd.DataFrame(data.data) if data.data else pd.DataFrame()
            teachers = sorted(df["prof"].dropna().unique().tolist())

# =====================================================
# CLASSEMENT DES PROFESSEURS
# =====================================================
st.header("Classement des professeurs")
if df.empty:
    st.info("Aucun avis disponible pour le moment.")
    st.stop()

cours_choisi = st.selectbox("Choisir un cours", sorted(df["cours"].unique()))
profil = st.selectbox("Profil étudiant", ["ordinaire","cote_r","apprentissage","chill","stress_minimiser","equite_focus"])

df_grouped = df.groupby(["prof","cours"], as_index=False)[numeric_cols].mean()
df_filtered = df_grouped[df_grouped["cours"] == cours_choisi].copy()

df_filtered["stress_inv"] = 10 - df_filtered["stress"]
df_filtered["impact_inv"] = 10 - df_filtered["impact_note"]
df_filtered["pedagogie"] = df_filtered[["clarte","organisation"]].mean(axis=1)
df_filtered["experience"] = df_filtered[["stress_inv","motivation"]].mean(axis=1)

poids = {
    "ordinaire": None,
    "cote_r": {"pedagogie":0.25,"impact":0.40,"equite":0.20,"aide":0.10,"experience":0.05},
    "apprentissage": {"pedagogie":0.45,"impact":0.15,"equite":0.15,"aide":0.15,"experience":0.10},
    "chill": {"pedagogie":0.30,"impact":0.20,"equite":0.15,"aide":0.15,"experience":0.20},
    "stress_minimiser": {"pedagogie":0.25,"impact":0.10,"equite":0.15,"aide":0.10,"experience":0.40},
    "equite_focus": {"pedagogie":0.20,"impact":0.10,"equite":0.40,"aide":0.10,"experience":0.20}
}

if profil == "ordinaire":
    df_filtered["score_final"] = df_filtered[["clarte","organisation","equite","aide","motivation","stress_inv","impact_inv"]].mean(axis=1)
else:
    p = poids[profil]
    df_filtered["score_final"] = (
        df_filtered["pedagogie"]*p["pedagogie"] +
        df_filtered["impact_inv"]*p["impact"] +
        df_filtered["equite"]*p["equite"] +
        df_filtered["aide"]*p["aide"] +
        df_filtered["experience"]*p["experience"]
    )

df_filtered = df_filtered.sort_values("score_final", ascending=False).reset_index(drop=True)
df_filtered.index += 1

st.subheader(f"Classement – {cours_choisi}")
st.table(df_filtered[["prof","score_final"]].round(2))

# =====================================================
# TOP 3 – GRAPHIQUE
# =====================================================
top3 = df_filtered.head(3)
if not top3.empty:
    st.subheader("🏆 Top 3 professeurs")
    colors = ["gold","silver","peru"][:len(top3)]
    fig, ax = plt.subplots()
    ax.barh(top3["prof"], top3["score_final"], color=colors)
    ax.invert_yaxis()
    ax.set_xlabel("Score final")
    st.pyplot(fig)
