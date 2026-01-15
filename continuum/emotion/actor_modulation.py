# continuum/emotion/actor_modulation.py

from typing import Dict
from continuum.emotion.state_machine import EmotionalState
from continuum.emotion.actor_profiles import ACTOR_MODULATION_PROFILES


def _clamp(x: float, lo: float = 0.0, hi: float = 2.0) -> float:
    return max(lo, min(hi, x))


def compute_base_modulation(state: EmotionalState) -> Dict[str, float]:
    """
    Global emotional → cognitive modulation.
    """
    s = state.as_dict()

    return {
        "warmth": _clamp(0.8 + s["joy"] * 0.4 - s["tension"] * 0.2),
        "creativity": _clamp(0.7 + s["curiosity"] * 0.6 - s["focus"] * 0.2),
        "assertiveness": _clamp(0.6 + s["confidence"] * 0.5 - s["tension"] * 0.3),
        "structure": _clamp(0.7 + s["focus"] * 0.5 + s["calm"] * 0.3),
        "verbosity": _clamp(0.8 + s["curiosity"] * 0.3 - s["fatigue"] * 0.4),
    }


def apply_actor_modulation(actor_name: str, state: EmotionalState) -> Dict[str, float]:
    """
    Combine global modulation with actor-specific profile.
    """
    base = compute_base_modulation(state)
    profile = ACTOR_MODULATION_PROFILES.get(actor_name, {})

    modulated: Dict[str, float] = {}
    for key, value in base.items():
        offset = profile.get(key, 0.0)
        modulated[key] = _clamp(value + offset * 0.5)  # profile as gentle bias

    return modulated