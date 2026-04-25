import random
import time
import json
from datetime import datetime

# Realistic ranges for agricultural sensors
SENSOR_RANGES = {
    "N":           (0, 140),    # Nitrogen kg/ha
    "P":           (5, 145),    # Phosphorus kg/ha
    "K":           (5, 205),    # Potassium kg/ha
    "temperature": (8, 44),     # Celsius
    "humidity":    (14, 100),   # %
    "ph":          (3.5, 9.5),  # pH
    "rainfall":    (20, 300),   # mm
}

# Simulated field profiles (different soil/climate scenarios)
FIELD_PROFILES = {
    "dry_field": {
        "N": (20, 60), "P": (10, 40), "K": (10, 50),
        "temperature": (30, 44), "humidity": (14, 35),
        "ph": (6.5, 8.5), "rainfall": (20, 80)
    },
    "optimal_field": {
        "N": (60, 100), "P": (40, 80), "K": (40, 80),
        "temperature": (20, 30), "humidity": (50, 80),
        "ph": (5.5, 7.0), "rainfall": (100, 200)
    },
    "wet_field": {
        "N": (80, 140), "P": (70, 130), "K": (80, 180),
        "temperature": (15, 25), "humidity": (80, 100),
        "ph": (4.0, 6.5), "rainfall": (200, 300)
    }
}

def simulate_sensors(profile="optimal_field"):
    """Generate one reading from simulated sensors."""
    ranges = FIELD_PROFILES.get(profile, FIELD_PROFILES["optimal_field"])
    reading = {
        key: round(random.uniform(*val), 2)
        for key, val in ranges.items()
    }
    reading["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reading["field_profile"] = profile
    return reading

def stream_sensors(interval=5, profile="optimal_field"):
    """Continuously stream sensor readings every `interval` seconds."""
    print(f"📡 Sensor stream started — profile: {profile}")
    while True:
        data = simulate_sensors(profile)
        yield data
        time.sleep(interval)

if __name__ == "__main__":
    print("🌱 Testing sensor simulation...")
    for profile in FIELD_PROFILES:
        reading = simulate_sensors(profile)
        print(f"\n[{profile}]")
        print(json.dumps(reading, indent=2))
