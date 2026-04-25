import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from sensors import simulate_sensors, FIELD_PROFILES
from ai_agent import run_analysis
from audio_generator import generate_audio

# Page config
st.set_page_config(
    page_title="Aquaterra",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1a472a, #2d6a4f);
        border-radius: 12px;
        padding: 16px;
        color: white;
        text-align: center;
        margin: 4px;
    }
    .status-critical { background-color: #ff4444; color: white; padding: 8px 16px; border-radius: 8px; font-weight: bold; }
    .status-low      { background-color: #ff8800; color: white; padding: 8px 16px; border-radius: 8px; font-weight: bold; }
    .status-optimal  { background-color: #00aa44; color: white; padding: 8px 16px; border-radius: 8px; font-weight: bold; }
    .status-excess   { background-color: #0066cc; color: white; padding: 8px 16px; border-radius: 8px; font-weight: bold; }
    .podcast-box { background: #f0f7f0; border-left: 4px solid #2d6a4f; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 13px; white-space: pre-wrap; }
    h1 { color: #1a472a !important; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "last_script" not in st.session_state:
    st.session_state.last_script = None
if "last_data" not in st.session_state:
    st.session_state.last_data = None

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/1a472a/ffffff?text=🌿+AQUATERRA", use_container_width=True)
    st.markdown("---")
    st.subheader("⚙️ Configuration")
    
    profile = st.selectbox(
        "Field Profile",
        options=list(FIELD_PROFILES.keys()),
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    auto_refresh = st.toggle("🔄 Auto-refresh (30s)", value=False)
    generate_audio_toggle = st.toggle("🎙️ Generate podcast audio", value=True)
    
    st.markdown("---")
    st.subheader("ℹ️ About")
    st.caption("Aquaterra monitors soil conditions and generates actionable recommendations for farmers through AI analysis and audio podcasts.")

# Header
st.title("🌿 Aquaterra — Smart Agricultural Monitoring")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Run analysis button
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
with col_btn1:
    run_btn = st.button("▶ Run Analysis", type="primary", use_container_width=True)
with col_btn2:
    clear_btn = st.button("🗑️ Clear History", use_container_width=True)

if clear_btn:
    st.session_state.history = []
    st.rerun()

# Run analysis
if run_btn or (auto_refresh and time.time() % 30 < 1):
    with st.spinner("🔬 Analyzing soil data..."):
        data = simulate_sensors(profile)
        analysis, script = run_analysis(data)
        
        # Generate audio
        audio_path = None
        if generate_audio_toggle:
            try:
                audio_path = generate_audio(script)
            except Exception as e:
                st.warning(f"Audio generation failed: {e}")
        
        # Save to history
        st.session_state.history.append({
            "timestamp": data["timestamp"],
            "data": data,
            "analysis": analysis,
            "script": script,
            "audio": audio_path
        })
        
        st.session_state.last_analysis = analysis
        st.session_state.last_script = script
        st.session_state.last_data = data

# Display latest results
if st.session_state.last_analysis:
    analysis = st.session_state.last_analysis
    data = st.session_state.last_data
    script = st.session_state.last_script

    st.markdown("---")
    st.subheader("📊 Latest Sensor Readings")
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    metrics = [
        (col1, "🌡️ Temp", f"{data['temperature']}°C"),
        (col2, "💧 Humidity", f"{data['humidity']}%"),
        (col3, "🧪 pH", f"{data['ph']}"),
        (col4, "🌧️ Rainfall", f"{data['rainfall']}mm"),
        (col5, "🟢 Nitrogen", f"{data['N']}"),
        (col6, "🔵 Phosphorus", f"{data['P']}"),
        (col7, "🟡 Potassium", f"{data['K']}"),
    ]
    for col, label, value in metrics:
        with col:
            st.metric(label=label, value=value)

    st.markdown("---")
    st.subheader("🤖 AI Analysis Results")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        irr = analysis["irrigation"]
        status_color = {"CRITICAL": "🔴", "LOW": "🟠", "OPTIMAL": "🟢", "EXCESS": "🔵"}.get(irr["status"], "⚪")
        st.markdown(f"**💧 Irrigation — {status_color} {irr['status']}**")
        st.info(irr["advice"])
        if irr["liters_per_m2"] > 0:
            st.metric("Required water", f"{irr['liters_per_m2']} L/m²")

    with col_b:
        ph = analysis["ph"]
        st.markdown(f"**🧪 Soil pH — {ph['emoji']} {ph['status']}**")
        st.info(ph["advice"])
        
        st.markdown("**🌱 Nutrients**")
        for n in analysis["nutrients"]:
            st.write(f"• {n}")

    with col_c:
        crop = analysis["crop"]
        st.markdown("**🌾 Recommended Crop**")
        st.success(f"**{crop['crop'].upper()}**")
        st.progress(crop["confidence"] / 100)
        st.caption(f"Model confidence: {crop['confidence']}%")

    # Podcast section
    st.markdown("---")
    st.subheader("📻 Generated Podcast")

    tab1, tab2 = st.tabs(["📄 Script", "🎧 Audio"])
    
    with tab1:
        st.markdown(f'<div class="podcast-box">{script}</div>', unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download Script",
            data=script,
            file_name=f"aquaterra_report_{data['timestamp'].replace(' ', '_')}.txt",
            mime="text/plain"
        )

    with tab2:
        # Find latest audio
        latest_audio = None
        if st.session_state.history:
            for entry in reversed(st.session_state.history):
                if entry.get("audio") and os.path.exists(entry["audio"]):
                    latest_audio = entry["audio"]
                    break
        
        if latest_audio:
            with open(latest_audio, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
            st.download_button(
                "⬇️ Download Podcast MP3",
                data=open(latest_audio, "rb").read(),
                file_name=os.path.basename(latest_audio),
                mime="audio/mp3"
            )
        else:
            st.info("Enable 'Generate podcast audio' in sidebar and run analysis to generate audio.")

# History chart
if len(st.session_state.history) > 1:
    st.markdown("---")
    st.subheader("📈 Historical Data")
    
    df = pd.DataFrame([{
        "Time": e["timestamp"],
        "Humidity (%)": e["data"]["humidity"],
        "Temperature (°C)": e["data"]["temperature"],
        "pH": e["data"]["ph"],
        "Rainfall (mm)": e["data"]["rainfall"],
    } for e in st.session_state.history])
    
    tab_h, tab_t, tab_p, tab_r = st.tabs(["💧 Humidity", "🌡️ Temperature", "🧪 pH", "🌧️ Rainfall"])
    with tab_h: st.line_chart(df.set_index("Time")["Humidity (%)"])
    with tab_t: st.line_chart(df.set_index("Time")["Temperature (°C)"])
    with tab_p: st.line_chart(df.set_index("Time")["pH"])
    with tab_r: st.line_chart(df.set_index("Time")["Rainfall (mm)"])

    st.subheader("📋 Full History")
    st.dataframe(df, use_container_width=True)

else:
    st.markdown("---")
    st.info("👆 Click **Run Analysis** to start the system and see live results.")
    st.markdown("""
    **How it works:**
    1. 🌱 **Sensors** simulate real soil data (humidity, pH, temperature, NPK, rainfall)
    2. 🤖 **AI Agent** analyzes the data using a trained Random Forest model
    3. 📻 **Podcast** is automatically generated with recommendations in French
    4. 🎧 **Audio** is converted to MP3 using text-to-speech
    """)

# Footer
st.markdown("---")
st.caption("🌿 Aquaterra — Transition Écologique & Dynamique Culturelle Artistique | Smart Agriculture Morocco")
