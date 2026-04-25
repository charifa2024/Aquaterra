import streamlit as st
import pandas as pd
import os, sys, time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from sensors import simulate_sensors, PROFILS
from ai_agent import run_analysis
from audio_generator import generate_audio
from rapport_pdf import generer_rapport

st.set_page_config(page_title="Aquaterra", page_icon="🌿", layout="wide")

st.markdown("""
<style>
.stMetric label { font-size: 12px !important; }
.bloc-vert { background:#e8f5e9; border-left:4px solid #2e7d32; padding:12px 16px; border-radius:6px; margin:6px 0; }
.bloc-rouge { background:#ffebee; border-left:4px solid #c62828; padding:12px 16px; border-radius:6px; margin:6px 0; }
.bloc-orange { background:#fff3e0; border-left:4px solid #e65100; padding:12px 16px; border-radius:6px; margin:6px 0; }
.bloc-bleu { background:#e3f2fd; border-left:4px solid #1565c0; padding:12px 16px; border-radius:6px; margin:6px 0; }
.edu-box { background:#f3e5f5; border-left:4px solid #6a1b9a; padding:10px 14px; border-radius:6px; margin:4px 0; font-size:13px; }
.podcast-box { background:#f1f8e9; border:1px solid #aed581; padding:16px; border-radius:8px; font-family:monospace; font-size:12px; white-space:pre-wrap; }
.titre-rapport { font-size:28px; font-weight:700; color:#1b5e20; margin:0; }
.sous-titre { font-size:14px; color:#555; margin-bottom:16px; }
</style>
""", unsafe_allow_html=True)

if "historique" not in st.session_state:
    st.session_state.historique = []
if "derniere_analyse" not in st.session_state:
    st.session_state.derniere_analyse = None
if "derniere_data" not in st.session_state:
    st.session_state.derniere_data = None
if "dernier_script" not in st.session_state:
    st.session_state.dernier_script = None

# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 Aquaterra")
    st.caption("Système intelligent de surveillance agricole")
    st.markdown("---")
    st.subheader("⚙️ Configuration")

    profil = st.selectbox(
        "Profil du champ",
        options=["Champ sec", "Champ optimal", "Champ humide"],
        index=1
    )
    profil_desc = {
        "Champ sec": "🔴 Sol sec — risque de sécheresse",
        "Champ optimal": "🟢 Conditions idéales",
        "Champ humide": "🔵 Sol saturé — risque d'inondation"
    }
    st.caption(profil_desc[profil])

    st.markdown("---")
    gen_audio = st.toggle("🎙️ Générer le podcast audio", value=True)
    gen_pdf   = st.toggle("📄 Générer le rapport PDF", value=True)

    st.markdown("---")
    st.subheader("ℹ️ À propos")
    st.caption(
        "Aquaterra surveille les conditions du sol et génère des recommandations "
        "agricoles via l'IA, diffusées sous forme de podcast audio en français."
    )

# ── Header ──────────────────────────────────────────────────────
st.markdown('<p class="titre-rapport">🌿 Aquaterra — Surveillance Agricole Intelligente</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sous-titre">Module : Transition Écologique & Dynamique Culturelle Artistique | Dernière mise à jour : {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 5])
with col1:
    lancer = st.button("▶ Analyser", type="primary", use_container_width=True)
with col2:
    effacer = st.button("🗑️ Effacer", use_container_width=True)

if effacer:
    st.session_state.historique = []
    st.session_state.derniere_analyse = None
    st.rerun()

# ── Analyse ─────────────────────────────────────────────────────
if lancer:
    with st.spinner("🔬 Analyse en cours..."):
        data = simulate_sensors(profil)
        analyse, script = run_analysis(data)

        audio_path = None
        if gen_audio:
            try:
                audio_path = generate_audio(script)
            except Exception as e:
                st.warning(f"Audio non généré : {e}")

        pdf_path = None
        if gen_pdf:
            try:
                pdf_path = generer_rapport(data, analyse)
            except Exception as e:
                st.warning(f"PDF non généré : {e}")

        st.session_state.historique.append({
            "timestamp": data["timestamp"],
            "data": data, "analyse": analyse,
            "script": script, "audio": audio_path, "pdf": pdf_path
        })
        st.session_state.derniere_analyse = analyse
        st.session_state.derniere_data    = data
        st.session_state.dernier_script   = script
        st.session_state.dernier_pdf      = pdf_path
        st.session_state.dernier_audio    = audio_path

# ── Résultats ────────────────────────────────────────────────────
if st.session_state.derniere_analyse:
    analyse = st.session_state.derniere_analyse
    data    = st.session_state.derniere_data
    script  = st.session_state.dernier_script

    st.markdown("---")
    st.subheader("📊 Données des capteurs")
    c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
    c1.metric("🌡️ Température", f"{data['temperature']}°C")
    c2.metric("💧 Humidité",    f"{data['humidity']}%")
    c3.metric("🧪 pH",          f"{data['ph']}")
    c4.metric("🌧️ Pluies",      f"{data['rainfall']}mm")
    c5.metric("🟢 Azote",       f"{data['N']}")
    c6.metric("🔵 Phosphore",   f"{data['P']}")
    c7.metric("🟡 Potassium",   f"{data['K']}")

    # ── Irrigation ──────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🤖 Résultats de l'analyse IA")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        irr = analyse["irrigation"]
        couleur_map = {"CRITIQUE": "rouge", "BAS": "orange", "OPTIMAL": "vert", "EXCÈS": "bleu"}
        cls = couleur_map.get(irr["statut"], "vert")
        st.markdown(f'<div class="bloc-{cls}"><b>💧 Irrigation — {irr["emoji"]} {irr["statut"]}</b><br>{irr["conseil"]}</div>', unsafe_allow_html=True)
        if irr["litres"] > 0:
            st.metric("Volume requis", f"{irr['litres']} L/m²")
        st.markdown(f'<div class="edu-box">📚 <b>Savoir :</b> {irr["education"]}</div>', unsafe_allow_html=True)

    with col_b:
        ph = analyse["ph"]
        cls_ph = "orange" if ph["statut"] in ["ACIDE","ALCALIN"] else "vert"
        st.markdown(f'<div class="bloc-{cls_ph}"><b>🧪 pH — {ph["emoji"]} {ph["statut"]}</b><br>{ph["conseil"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="edu-box">📚 <b>Savoir :</b> {ph["education"]}</div>', unsafe_allow_html=True)

        st.markdown("<br>**🌱 Nutriments**", unsafe_allow_html=True)
        for n in analyse["nutriments"]:
            em = "⚠️" if n["statut"] == "BAS" else "✅"
            cls_n = "orange" if n["statut"] == "BAS" else "vert"
            st.markdown(f'<div class="bloc-{cls_n}"><b>{em} {n["nutriment"]}</b> — {n["valeur"]}<br>{n["conseil"]}</div>', unsafe_allow_html=True)
            if n["education"]:
                st.markdown(f'<div class="edu-box">📚 {n["education"]}</div>', unsafe_allow_html=True)

    with col_c:
        culture = analyse["culture"]
        st.markdown('<div class="bloc-vert"><b>🌾 Culture recommandée par l\'IA</b></div>', unsafe_allow_html=True)
        st.markdown(f"### {culture['culture_fr'].upper()}")
        st.progress(culture["confiance"] / 100)
        st.caption(f"Confiance du modèle : {culture['confiance']}%")

    # ── Podcast ──────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📻 Podcast Agricole Généré Automatiquement")

    tab_script, tab_audio, tab_rapport = st.tabs(["📄 Script du podcast", "🎧 Audio", "📥 Rapport PDF"])

    with tab_script:
        st.markdown(f'<div class="podcast-box">{script}</div>', unsafe_allow_html=True)
        st.download_button(
            "⬇️ Télécharger le script",
            data=script,
            file_name=f"podcast_aquaterra_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

    with tab_audio:
        audio_path = st.session_state.get("dernier_audio")
        if audio_path and os.path.exists(audio_path):
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                "⬇️ Télécharger le podcast MP3",
                data=audio_bytes,
                file_name=os.path.basename(audio_path),
                mime="audio/mp3"
            )
        else:
            st.info("Activez 'Générer le podcast audio' dans la barre latérale et relancez l'analyse.")

    with tab_rapport:
        pdf_path = st.session_state.get("dernier_pdf")
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.success(f"✅ Rapport PDF généré avec succès !")
            st.download_button(
                label="⬇️ Télécharger le rapport PDF complet",
                data=pdf_bytes,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
                type="primary"
            )
            st.caption("Le rapport contient : données capteurs, analyse irrigation, pH, nutriments, culture recommandée et guide éducatif complet.")
        else:
            st.info("Activez 'Générer le rapport PDF' dans la barre latérale et relancez l'analyse.")

# ── Historique ───────────────────────────────────────────────────
if len(st.session_state.historique) > 1:
    st.markdown("---")
    st.subheader("📈 Historique des mesures")
    df = pd.DataFrame([{
        "Heure":        e["timestamp"],
        "Humidité (%)": e["data"]["humidity"],
        "Température (°C)": e["data"]["temperature"],
        "pH":           e["data"]["ph"],
        "Pluies (mm)":  e["data"]["rainfall"],
        "Profil":       e["data"].get("profil", "—"),
    } for e in st.session_state.historique])

    t1, t2, t3, t4 = st.tabs(["💧 Humidité", "🌡️ Température", "🧪 pH", "🌧️ Pluies"])
    with t1: st.line_chart(df.set_index("Heure")["Humidité (%)"])
    with t2: st.line_chart(df.set_index("Heure")["Température (°C)"])
    with t3: st.line_chart(df.set_index("Heure")["pH"])
    with t4: st.line_chart(df.set_index("Heure")["Pluies (mm)"])
    st.dataframe(df, use_container_width=True)
else:
    st.markdown("---")
    st.info("👆 Cliquez sur **Analyser** pour démarrer le système et voir les résultats en temps réel.")
    st.markdown("""
    **Comment ça fonctionne :**
    1. 🌱 Les **capteurs simulés** génèrent des données réalistes du sol (humidité, pH, température, NPK, pluies)
    2. 🤖 L'**agent IA** analyse les données avec un modèle Random Forest entraîné
    3. 📻 Un **podcast en français** est généré automatiquement avec conseils et explications
    4. 🎧 L'**audio MP3** est créé par synthèse vocale et téléchargeable
    5. 📄 Un **rapport PDF** complet et éducatif est généré et téléchargeable
    """)

st.markdown("---")
st.caption("🌿 Aquaterra — Transition Écologique & Dynamique Culturelle Artistique | Agriculture Durable au Maroc")