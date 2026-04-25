import random
import time
import json
from datetime import datetime

PROFILS = {
    "Champ sec": {
        "N": (20, 60), "P": (10, 40), "K": (10, 50),
        "temperature": (30, 44), "humidity": (14, 35),
        "ph": (6.5, 8.5), "rainfall": (20, 80)
    },
    "Champ optimal": {
        "N": (60, 100), "P": (40, 80), "K": (40, 80),
        "temperature": (20, 30), "humidity": (50, 80),
        "ph": (5.5, 7.0), "rainfall": (100, 200)
    },
    "Champ humide": {
        "N": (80, 140), "P": (70, 130), "K": (80, 180),
        "temperature": (15, 25), "humidity": (80, 100),
        "ph": (4.0, 6.5), "rainfall": (200, 300)
    }
}

# For backward compatibility with English keys
PROFILS["dry_field"]     = PROFILS["Champ sec"]
PROFILS["optimal_field"] = PROFILS["Champ optimal"]
PROFILS["wet_field"]     = PROFILS["Champ humide"]

FIELD_PROFILES = PROFILS

def simulate_sensors(profil="Champ optimal"):
    ranges = PROFILS.get(profil, PROFILS["Champ optimal"])
    reading = {key: round(random.uniform(*val), 2) for key, val in ranges.items()}
    reading["timestamp"] = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
    reading["profil"] = profil
    reading["field_profile"] = profil
    return reading

def stream_sensors(interval=5, profil="Champ optimal"):
    print(f"📡 Flux capteurs démarré — profil : {profil}")
    while True:
        yield simulate_sensors(profil)
        time.sleep(interval)