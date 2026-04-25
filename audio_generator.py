from gtts import gTTS
import os
from datetime import datetime

def generate_audio(script, filename=None, lang="fr"):
    if filename is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"podcast_{ts}.mp3"
    os.makedirs("podcasts", exist_ok=True)
    filepath = os.path.join("podcasts", filename)
    clean = script
    for ch in ["🎙️","📊","💧","🧪","🌱","🌾","🔴","🟠","🟢","🔵","⚠️","✅","•","---","="]:
        clean = clean.replace(ch, "")
    tts = gTTS(text=clean, lang=lang, slow=False)
    tts.save(filepath)
    print(f"🎧 Audio sauvegardé : {filepath}")
    return filepath