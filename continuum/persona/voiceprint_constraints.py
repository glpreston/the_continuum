# continuum/personavoiceprint_constraints.py  

import re
from continuum.persona.voiceprint_loader import voiceprint_loader


def apply_voiceprint_constraints(text: str, dominant_emotion: str) -> str:
    pacing_rules = voiceprint_loader.get_pacing_rules()
    forbidden = voiceprint_loader.get_forbidden_elements()

    for term in forbidden:
        if term.lower() in text.lower():
            text = re.sub(r"\bobviously\b", "notably", text)
            text = text.replace("clearly you", "it may seem")

    if dominant_emotion in ("sadness", "fatigue", "tension"):
        if pacing_rules.get("high_emotion_line_breaks", False) and "\n\n" not in text:
            text = re.sub(r"\. (?=[A-Z])", ".\n\n", text)

    return text