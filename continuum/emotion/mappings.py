# continuum/emotion/mappings.py

from typing import Dict

# Map emotion labels → emotional state deltas
# These are continuous emotional influences, not discrete states.
EMOTION_DELTA_MAP: Dict[str, Dict[str, float]] = {
    "joy":       {"joy": +0.4, "curiosity": +0.2, "calm": +0.1},
    "sadness":   {"joy": -0.4, "confidence": -0.2, "fatigue": +0.2},
    "anger":     {"tension": +0.5, "calm": -0.3, "confidence": +0.1},
    "fear":      {"tension": +0.5, "confidence": -0.3, "calm": -0.2},
    "anxiety":   {"tension": +0.4, "calm": -0.3, "confidence": -0.2},
    "confusion": {"focus": -0.3, "confidence": -0.2, "curiosity": +0.1},
    "curiosity": {"curiosity": +0.5, "focus": +0.2, "joy": +0.1},
    "disgust":   {"tension": +0.3, "joy": -0.3},
    "neutral":   {},
}

def build_delta_from_labels(
    labels: Dict[str, float],
    scale: float = 1.0,
) -> Dict[str, float]:
    """
    Convert emotion labels + intensities into a delta vector
    for the emotional state machine.
    """
    delta: Dict[str, float] = {}

    for label, intensity in labels.items():
        base = EMOTION_DELTA_MAP.get(label.lower(), {})
        for dim, value in base.items():
            delta[dim] = delta.get(dim, 0.0) + value * intensity * scale

    return delta