# continuum/meta/aria_emotional_blending.py

from typing import Dict
from continuum.emotion.state_machine import EmotionalState


def compute_aria_style(state: EmotionalState) -> Dict[str, float]:
    """
    Convert emotional state → Aria's tone modulation.
    Values are gentle multipliers (0.5–1.5).
    """

    s = state.as_dict()

    return {
        "warmth": 1.0 + s["joy"] * 0.4 - s["tension"] * 0.2,
        "clarity": 1.0 + s["focus"] * 0.3 + s["calm"] * 0.3,
        "brevity": 1.0 + s["fatigue"] * 0.5,
        "creativity": 1.0 + s["curiosity"] * 0.5 + s["joy"] * 0.2,

        # FIXED: sadness is not a dimension — use low joy + low confidence instead
        "softness": 1.0
            + (1.0 - s["joy"]) * 0.3
            + (1.0 - s["confidence"]) * 0.2
            + s["tension"] * 0.1,
    }