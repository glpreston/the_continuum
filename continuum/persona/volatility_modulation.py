# continuum/personavolatility_modulation.py  
import re
from continuum.persona.emotional_memory import EmotionalMemory


def apply_volatility_modulation(text: str, emotional_memory: EmotionalMemory) -> str:
    volatility = emotional_memory.volatility

    if volatility > 0.55:
        text = re.sub(r"\bperhaps\b", "let’s take this one step at a time", text)
        text = re.sub(r"\bclearly\b", "we can see", text)
        return text

    if volatility < 0.25:
        text = text.replace("—", " — ")
        text = text.replace(". ", ".\n")

    return text