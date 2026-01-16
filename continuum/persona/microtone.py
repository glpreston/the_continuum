#continuum/persona/microtone.py
import re
from continuum.emotion.state_machine import EmotionalState


def apply_microtone(text: str, emotional_state: EmotionalState) -> str:
    state = emotional_state.as_dict()

    curiosity = state.get("curiosity", 0)
    calm = state.get("calm", 0)
    tension = state.get("tension", 0)
    confidence = state.get("confidence", 0)
    fatigue = state.get("fatigue", 0)

    if curiosity > 0.45:
        text = re.sub(r"\bHere is\b", "Here’s one way to see this", text)
        text = re.sub(r"\bThis\b", "One angle on this", text, count=1)

    if calm > 0.45:
        text = text.replace("However", "At the same time")
        text = text.replace("But", "That said")

    if tension > 0.45:
        text = re.sub(r"\bThis means\b", "This suggests", text)
        text = re.sub(r"\bIt is\b", "It may be", text)

    if confidence > 0.45:
        text = re.sub(r"\bperhaps\b", "clearly", text)
        text = re.sub(r"\bmaybe\b", "notably", text)

    if fatigue > 0.35 and "\n\n" not in text:
        text = re.sub(r"\. (?=[A-Z])", ".\n\n", text)

    return text