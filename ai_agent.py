import joblib
import numpy as np
import pandas as pd
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
import json
from datetime import datetime

# Load trained model and encoder
try:
    model = joblib.load("crop_model.pkl")
    le = joblib.load("label_encoder.pkl")
    MODEL_LOADED = True
    print("✅ AI model loaded successfully")
except FileNotFoundError:
    MODEL_LOADED = False
    print("⚠️  Model not found. Run train_model.py first.")

# Irrigation thresholds
IRRIGATION_THRESHOLDS = {
    "critical":  {"humidity": 25, "rainfall": 50},
    "low":       {"humidity": 45, "rainfall": 100},
    "optimal":   {"humidity": 70, "rainfall": 180},
}

def analyze_irrigation(data):
    """Determine irrigation status and recommendation."""
    h = data["humidity"]
    r = data["rainfall"]

    if h < IRRIGATION_THRESHOLDS["critical"]["humidity"] or r < IRRIGATION_THRESHOLDS["critical"]["rainfall"]:
        status = "CRITICAL"
        liters = round((100 - h) * 0.25, 1)
        advice = f"Irrigate immediately with {liters}L/m². Soil is critically dry."
        emoji = "🔴"
    elif h < IRRIGATION_THRESHOLDS["low"]["humidity"] or r < IRRIGATION_THRESHOLDS["low"]["rainfall"]:
        status = "LOW"
        liters = round((70 - h) * 0.15, 1)
        advice = f"Irrigate with {liters}L/m² within 24 hours."
        emoji = "🟠"
    elif h > 85 and r > 220:
        status = "EXCESS"
        liters = 0
        advice = "Soil is over-saturated. Stop irrigation. Check drainage."
        emoji = "🔵"
    else:
        status = "OPTIMAL"
        liters = 0
        advice = "Soil moisture is optimal. No irrigation needed."
        emoji = "🟢"

    return {"status": status, "liters_per_m2": liters, "advice": advice, "emoji": emoji}

def analyze_ph(data):
    """Analyze soil pH and give correction advice."""
    ph = data["ph"]
    if ph < 5.5:
        return {"status": "ACIDIC", "advice": "Add agricultural lime (2-3 kg/m²) to raise pH.", "emoji": "⚠️"}
    elif ph > 7.5:
        return {"status": "ALKALINE", "advice": "Add sulfur or acidic compost to lower pH.", "emoji": "⚠️"}
    else:
        return {"status": "OPTIMAL", "advice": "pH level is ideal for most crops.", "emoji": "✅"}

def analyze_nutrients(data):
    """Analyze NPK nutrient levels."""
    n, p, k = data["N"], data["P"], data["K"]
    alerts = []
    if n < 30: alerts.append("Low Nitrogen — add organic compost or urea fertilizer.")
    if p < 20: alerts.append("Low Phosphorus — add superphosphate fertilizer.")
    if k < 20: alerts.append("Low Potassium — add potassium chloride.")
    if not alerts:
        alerts.append("NPK levels are balanced and sufficient.")
    return alerts

def predict_crop(data):
    """Predict the best crop for current soil conditions."""
    if not MODEL_LOADED:
        return "Model not available"
    features = pd.DataFrame([{"N": data["N"], "P": data["P"], "K": data["K"], "temperature": data["temperature"], "humidity": data["humidity"], "ph": data["ph"], "rainfall": data["rainfall"]}])
    features_list = [[
        data["N"], data["P"], data["K"],
        data["temperature"], data["humidity"],
        data["ph"], data["rainfall"]
    ]]
    pred = model.predict(features)[0]
    proba = model.predict_proba(features)[0]
    confidence = round(max(proba) * 100, 1)
    crop_name = le.inverse_transform([pred])[0]
    return {"crop": crop_name, "confidence": confidence}

def generate_podcast_script(data, analysis):
    """Generate a podcast script from the analysis results."""
    irrigation = analysis["irrigation"]
    ph = analysis["ph"]
    nutrients = analysis["nutrients"]
    crop = analysis["crop"]
    ts = data["timestamp"]

    script = f"""
🎙️ AQUATERRA — DAILY FIELD REPORT
Date: {ts}
Field Profile: {data.get("field_profile", "Unknown").replace("_", " ").title()}

---

Bonjour à tous les agriculteurs !
Voici le rapport quotidien de vos champs, analysé par le système Aquaterra.

📊 ÉTAT DU SOL :
Température : {data['temperature']}°C
Humidité du sol : {data['humidity']}%
Niveau de pH : {data['ph']}
Précipitations récentes : {data['rainfall']} mm

💧 IRRIGATION : {irrigation['emoji']} {irrigation['status']}
{irrigation['advice']}

🧪 ÉTAT DU PH : {ph['emoji']} {ph['status']}
{ph['advice']}

🌱 NUTRIMENTS :
""" + "\n".join(f"• {n}" for n in nutrients) + f"""

🌾 CULTURE RECOMMANDÉE :
Le système recommande de planter : {crop['crop'].upper()}
Niveau de confiance : {crop['confidence']}%

---
Bonne journée et bonne récolte !
Aquaterra — La technologie au service de la terre.
"""
    return script.strip()

def run_analysis(sensor_data):
    """Full analysis pipeline: sensor data → complete analysis + podcast script."""
    irrigation = analyze_irrigation(sensor_data)
    ph        = analyze_ph(sensor_data)
    nutrients = analyze_nutrients(sensor_data)
    crop      = predict_crop(sensor_data)

    analysis = {
        "irrigation": irrigation,
        "ph": ph,
        "nutrients": nutrients,
        "crop": crop,
        "timestamp": sensor_data["timestamp"]
    }

    script = generate_podcast_script(sensor_data, analysis)
    return analysis, script

if __name__ == "__main__":
    from sensors import simulate_sensors
    print("\n🔬 Running test analysis...\n")
    for profile in ["dry_field", "optimal_field", "wet_field"]:
        data = simulate_sensors(profile)
        analysis, script = run_analysis(data)
        print(script)
        print("\n" + "="*60 + "\n")
