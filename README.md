# 🌿 AQUATERRA — Setup Guide

## Your project files:
```
aquaterra/
├── train_model.py        ← Train the AI model (run once)
├── sensors.py            ← Sensor simulation module
├── ai_agent.py           ← Analysis + podcast script generator
├── audio_generator.py    ← Text-to-speech podcast audio
├── dashboard.py          ← Main Streamlit dashboard (run this!)
├── Crop_recommendation.csv
├── crop_model.pkl        ← Trained model (generated)
└── label_encoder.pkl     ← Label encoder (generated)
```

## ▶️ How to run:

### Step 1 — Install dependencies
```bash
cd aquaterra
python -m venv venv
venv\Scripts\activate        # Windows
pip install pandas scikit-learn numpy streamlit gtts joblib
```

### Step 2 — Train the model (only once)
```bash
python train_model.py
```

### Step 3 — Launch the dashboard
```bash
streamlit run dashboard.py
```
→ Opens automatically at http://localhost:8501

## 🔄 The automatic pipeline:
1. Click **Run Analysis** in the dashboard
2. Sensors generate soil data automatically
3. AI model analyzes and recommends crops
4. Podcast script is generated in French
5. Audio MP3 is created and playable in the dashboard

## 🎛️ Field Profiles:
- **Dry Field** — low humidity, high temperature (triggers irrigation alerts)
- **Optimal Field** — balanced conditions
- **Wet Field** — high humidity, risk of over-saturation
