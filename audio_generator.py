from gtts import gTTS
import os
import re
import unicodedata
from datetime import datetime


# Characters and patterns that confuse gTTS or produce robotic pauses
_STRIP_CHARS = [
    "🎙️","📊","💧","🧪","🌱","🌾","🔴","🟠","🟢","🔵","⚠️","✅",
    "•","---","===","–","—",   # dashes and dividers
    "L/m²", "kg/m²",           # units that gTTS mispronounces → replaced below
]

_REPLACEMENTS = [
    (r"L/m²",    "litres par mètre carré"),
    (r"kg/m²",   "kilos par mètre carré"),
    (r"46-0-0",  "quarante-six zéro zéro"),
    (r"(\d+)%",  r"\1 pourcent"),
    (r"(\d+)°C", r"\1 degrés Celsius"),
    # Remove leftover symbols
    (r"[—–\-]{2,}", " "),
    (r"[^\S\r\n]{2,}", " "),    # collapse multiple spaces
]


def _clean_for_tts(text: str) -> str:
    """Return a version of *text* safe for gTTS French synthesis."""
    # 1. Apply word-level replacements first (order matters)
    for pattern, repl in _REPLACEMENTS:
        text = re.sub(pattern, repl, text)

    # 2. Strip known problematic character sequences
    for ch in _STRIP_CHARS:
        text = text.replace(ch, " ")

    # 3. Remove any remaining non-BMP / emoji characters
    #    (keeps accented Latin letters, punctuation, digits)
    cleaned = []
    for char in text:
        cat = unicodedata.category(char)
        # Keep letters (L*), numbers (N*), punctuation (P*), spaces (Z*), separators
        if cat.startswith(("L", "N", "P", "Z")) or char in ("\n", " "):
            cleaned.append(char)
        else:
            cleaned.append(" ")
    text = "".join(cleaned)

    # 4. Collapse runs of whitespace / blank lines
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def generate_audio(script: str, filename: str = None, lang: str = "fr") -> str:
    if filename is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"podcast_{ts}.mp3"

    os.makedirs("podcasts", exist_ok=True)
    filepath = os.path.join("podcasts", filename)

    clean = _clean_for_tts(script)

    tts = gTTS(text=clean, lang=lang, slow=False)
    tts.save(filepath)
    print(f"🎧 Audio sauvegardé : {filepath}")
    return filepath