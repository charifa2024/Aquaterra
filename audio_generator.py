from gtts import gTTS
import os
from datetime import datetime

def generate_audio(script, filename=None, lang="fr"):
    """Convert podcast script to audio MP3 file."""
    if filename is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"podcast_{ts}.mp3"

    os.makedirs("podcasts", exist_ok=True)
    filepath = os.path.join("podcasts", filename)

    # Clean script for TTS (remove emojis and markdown symbols)
    clean = script
    for char in ["🎙️", "📊", "💧", "🧪", "🌱", "🌾", "🔴", "🟠", "🟢", "🔵", "⚠️", "✅", "•", "---", "="]:
        clean = clean.replace(char, "")

    tts = gTTS(text=clean, lang=lang, slow=False)
    tts.save(filepath)
    print(f"🎧 Audio saved: {filepath}")
    return filepath

if __name__ == "__main__":
    test_script = """
    Bonjour à tous les agriculteurs !
    Voici le rapport quotidien de vos champs.
    L'humidité du sol est à 35 pourcent.
    Il est recommandé d'irriguer immédiatement avec 8 litres par mètre carré.
    La culture recommandée est le maïs avec un niveau de confiance de 94 pourcent.
    Bonne journée et bonne récolte !
    """
    path = generate_audio(test_script)
    print(f"✅ Test audio generated: {path}")
