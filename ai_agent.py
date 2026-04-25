import joblib
import numpy as np
import pandas as pd
import json
from datetime import datetime

try:
    model = joblib.load("crop_model.pkl")
    le = joblib.load("label_encoder.pkl")
    MODEL_LOADED = True
except FileNotFoundError:
    MODEL_LOADED = False

SEUILS = {
    "critique": {"humidite": 25, "pluies": 50},
    "bas":      {"humidite": 45, "pluies": 100},
    "optimal":  {"humidite": 70, "pluies": 180},
}

CULTURES_FR = {
    "rice": "Riz", "maize": "Maïs", "wheat": "Blé", "cotton": "Coton",
    "mango": "Mangue", "banana": "Banane", "grapes": "Raisin",
    "apple": "Pomme", "tomato": "Tomate", "onion": "Oignon",
    "mothbeans": "Haricots Moth", "mungbean": "Haricot Mungo",
    "blackgram": "Haricot Noir", "lentil": "Lentille",
    "pomegranate": "Grenade", "watermelon": "Pastèque",
    "muskmelon": "Melon", "papaya": "Papaye", "coconut": "Noix de coco",
    "jute": "Jute", "coffee": "Café", "pigeonpeas": "Pois Cajan",
    "kidneybeans": "Haricot Rouge", "chickpea": "Pois Chiche",
}

def analyser_irrigation(data):
    h = data["humidity"]
    r = data["rainfall"]
    if h < SEUILS["critique"]["humidite"] or r < SEUILS["critique"]["pluies"]:
        litres = round((100 - h) * 0.25, 1)
        return {
            "statut": "CRITIQUE", "emoji": "🔴",
            "conseil": f"Irriguer immédiatement avec {litres}L/m². Le sol est dangereusement sec.",
            "litres": litres,
            "education": (
                "L'humidité du sol est essentielle à la survie des plantes. En dessous de 25%, "
                "les racines ne peuvent plus absorber l'eau ni les nutriments. Les cellules végétales "
                "perdent leur turgescence et la plante commence à se faner. Une irrigation rapide "
                "est indispensable pour éviter des pertes irréversibles de récolte."
            )
        }
    elif h < SEUILS["bas"]["humidite"] or r < SEUILS["bas"]["pluies"]:
        litres = round((70 - h) * 0.15, 1)
        return {
            "statut": "BAS", "emoji": "🟠",
            "conseil": f"Irriguer avec {litres}L/m² dans les 24 heures.",
            "litres": litres,
            "education": (
                "Un niveau d'humidité bas ralentit la croissance et réduit le rendement des cultures. "
                "Les plantes en stress hydrique produisent moins de fruits et sont plus vulnérables "
                "aux maladies et aux parasites. Une irrigation préventive protège votre récolte."
            )
        }
    elif h > 85 and r > 220:
        return {
            "statut": "EXCÈS", "emoji": "🔵",
            "conseil": "Arrêter l'irrigation. Vérifier le drainage du sol.",
            "litres": 0,
            "education": (
                "Un excès d'eau dans le sol peut provoquer l'asphyxie des racines en empêchant "
                "l'oxygène d'atteindre les zones racinaires. Cela favorise aussi le développement "
                "de champignons et de maladies comme la pourriture des racines."
            )
        }
    else:
        return {
            "statut": "OPTIMAL", "emoji": "🟢",
            "conseil": "Niveau d'humidité idéal. Aucune irrigation nécessaire.",
            "litres": 0,
            "education": (
                "Un sol bien hydraté (50-80%) permet aux racines d'absorber efficacement l'eau "
                "et les nutriments dissous. C'est dans ces conditions que la photosynthèse et "
                "la croissance cellulaire sont les plus actives."
            )
        }

def analyser_ph(data):
    ph = data["ph"]
    if ph < 5.5:
        return {
            "statut": "ACIDE", "emoji": "⚠️",
            "conseil": f"pH = {ph:.1f} — Ajouter de la chaux agricole (2-3 kg/m²).",
            "education": (
                "Un sol trop acide bloque l'absorption de nutriments essentiels comme le phosphore, "
                "le calcium et le magnésium. La chaux agricole neutralise l'acidité progressivement "
                "sur 4 à 8 semaines."
            )
        }
    elif ph > 7.5:
        return {
            "statut": "ALCALIN", "emoji": "⚠️",
            "conseil": f"pH = {ph:.1f} — Ajouter du soufre agricole ou du compost acide.",
            "education": (
                "Un sol trop alcalin rend le fer, le manganèse et le zinc indisponibles pour les plantes, "
                "provoquant une chlorose. Le soufre élémentaire est oxydé par les bactéries du sol "
                "pour former de l'acide sulfurique, abaissant naturellement le pH."
            )
        }
    else:
        return {
            "statut": "OPTIMAL", "emoji": "✅",
            "conseil": f"pH = {ph:.1f} — Niveau idéal pour la majorité des cultures.",
            "education": (
                "Un pH entre 5.5 et 7.5 est la zone de confort pour la plupart des cultures. "
                "Dans cette plage, tous les nutriments essentiels sont solubles et accessibles aux racines."
            )
        }

def analyser_nutriments(data):
    n, p, k = data["N"], data["P"], data["K"]
    resultats = []
    if n < 30:
        resultats.append({
            "nutriment": "Azote (N)", "statut": "BAS", "valeur": n,
            "conseil": "Appliquer de l'urée (46-0-0) ou du compost organique.",
            "education": "L'azote est le moteur de la croissance végétative. Il entre dans la composition de la chlorophylle et des protéines. Un manque se manifeste par un jaunissement des vieilles feuilles."
        })
    else:
        resultats.append({"nutriment": "Azote (N)", "statut": "OK", "valeur": n, "conseil": "Niveau suffisant.", "education": ""})
    if p < 20:
        resultats.append({
            "nutriment": "Phosphore (P)", "statut": "BAS", "valeur": p,
            "conseil": "Appliquer du superphosphate ou de la farine d'os.",
            "education": "Le phosphore est indispensable au développement des racines, à la floraison et à la fructification."
        })
    else:
        resultats.append({"nutriment": "Phosphore (P)", "statut": "OK", "valeur": p, "conseil": "Niveau suffisant.", "education": ""})
    if k < 20:
        resultats.append({
            "nutriment": "Potassium (K)", "statut": "BAS", "valeur": k,
            "conseil": "Appliquer du chlorure de potassium ou des cendres de bois.",
            "education": "Le potassium régule l'ouverture des stomates et améliore la résistance aux maladies."
        })
    else:
        resultats.append({"nutriment": "Potassium (K)", "statut": "OK", "valeur": k, "conseil": "Niveau suffisant.", "education": ""})
    return resultats

def predire_culture(data):
    if not MODEL_LOADED:
        return {"culture": "non disponible", "culture_fr": "Non disponible", "confiance": 0}
    features = pd.DataFrame([{
        "N": data["N"], "P": data["P"], "K": data["K"],
        "temperature": data["temperature"], "humidity": data["humidity"],
        "ph": data["ph"], "rainfall": data["rainfall"]
    }])
    pred = model.predict(features)[0]
    proba = model.predict_proba(features)[0]
    confiance = round(max(proba) * 100, 1)
    culture_en = le.inverse_transform([pred])[0]
    culture_fr = CULTURES_FR.get(culture_en, culture_en.capitalize())
    return {"culture": culture_en, "culture_fr": culture_fr, "confiance": confiance}

def generer_script_podcast(data, analyse):
    irrigation = analyse["irrigation"]
    ph         = analyse["ph"]
    nutriments = analyse["nutriments"]
    culture    = analyse["culture"]
    profil     = data.get("profil", "Champ standard")
    ts         = data["timestamp"]

    alertes = []
    if irrigation["statut"] in ["CRITIQUE", "BAS"]:
        alertes.append(f"alerte irrigation {irrigation['statut'].lower()}")
    if ph["statut"] in ["ACIDE", "ALCALIN"]:
        alertes.append(f"pH {ph['statut'].lower()}")
    for n in nutriments:
        if n["statut"] == "BAS":
            alertes.append(f"manque de {n['nutriment'].split()[0].lower()}")

    intro_alerte = f"Attention ! Des alertes ont été détectées : {', '.join(alertes)}. " if alertes else ""

    lignes_nutriments = "\n".join([
        f"{n['nutriment']} : statut {n['statut']}. {n['conseil']} {n['education']}"
        for n in nutriments
    ])

    script = f"""Bonjour à tous les agriculteurs ! Bienvenue sur Aquaterra, votre système intelligent de surveillance agricole.

Nous sommes le {ts}. Profil du champ analysé : {profil}.

{intro_alerte}

Voici le rapport complet de vos champs.

Premièrement, les données des capteurs.
Température : {data['temperature']} degrés Celsius.
Humidité du sol : {data['humidity']} pourcent.
pH du sol : {data['ph']}.
Précipitations : {data['rainfall']} millimètres.
Azote : {data['N']}, Phosphore : {data['P']}, Potassium : {data['K']}.

Deuxièmement, l'irrigation.
Statut : {irrigation['statut']}. {irrigation['conseil']}
Information : {irrigation['education']}

Troisièmement, le pH du sol.
Statut : {ph['statut']}. {ph['conseil']}
Information : {ph['education']}

Quatrièmement, les nutriments.
{lignes_nutriments}

Cinquièmement, la culture recommandée.
Le système recommande de planter : {culture['culture_fr']}, avec une confiance de {culture['confiance']} pourcent.

Aquaterra vous accompagne chaque jour pour une agriculture durable et intelligente.
Prenez soin de votre terre, elle prendra soin de vous.
Bonne journée et bonne récolte !"""
    return script.strip()

def run_analysis(sensor_data):
    sensor_data["timestamp"] = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
    irrigation = analyser_irrigation(sensor_data)
    ph         = analyser_ph(sensor_data)
    nutriments = analyser_nutriments(sensor_data)
    culture    = predire_culture(sensor_data)
    analyse = {
        "irrigation": irrigation, "ph": ph,
        "nutriments": nutriments, "culture": culture,
        "timestamp": sensor_data["timestamp"]
    }
    script = generer_script_podcast(sensor_data, analyse)
    return analyse, script