# continuum/personatone_prefix.py  
from continuum.emotion.state_machine import EmotionalState


def compute_dominant_emotion(emotional_state: EmotionalState) -> str:
    state_dict = emotional_state.as_dict()
    filtered = {k: v for k, v in state_dict.items() if k != "fatigue"}

    if not filtered:
        return "neutral"

    values = list(filtered.values())
    max_val = max(values)
    min_val = min(values)

    if max_val - min_val < 0.02:
        return "neutral"

    return max(filtered, key=filtered.get)


def tone_prefix(dominant: str, volatility: float, confidence: float) -> str:
    if volatility > 0.55:
        return "Let’s slow down and take this step by step. "

    if dominant in ("sadness", "fatigue"):
        return "I’m moving gently with you here. "

    if dominant == "confusion":
        return "Let’s bring some clarity to this. "

    if dominant in ("anxiety", "nervousness"):
        return "We can keep things grounded. "

    if dominant == "curiosity":
        return "Let’s explore this together. "

    return ""