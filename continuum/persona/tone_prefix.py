# continuum/persona/tone_prefix.py

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
    """
    Fusion 2.1: emotional modulation should NOT prepend sentences.
    This function now returns an empty string so the fused text
    remains clean and neutral before rewriting.
    """
    return ""