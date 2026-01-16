# continuum/emotion/state_machine.py

from dataclasses import dataclass
from typing import Dict


@dataclass
class EmotionalState:
    joy: float = 0.5
    calm: float = 0.5
    focus: float = 0.5
    tension: float = 0.5
    curiosity: float = 0.5
    fatigue: float = 0.0
    confidence: float = 0.5   # baseline confidence

    # ---------------------------------------------------------
    # Computed properties (EI‑2.0)
    # ---------------------------------------------------------
    @property
    def volatility(self) -> float:
        """
        Volatility = L1 distance between this state and previous state.
        If no previous state exists, volatility = 0.
        """
        prev = getattr(self, "_prev_state", None)
        if prev is None:
            return 0.0

        keys = ["joy", "calm", "focus", "tension", "curiosity", "fatigue"]
        diffs = [abs(getattr(self, k) - getattr(prev, k)) for k in keys]
        return sum(diffs)

    @property
    def confidence_level(self) -> float:
        """
        Confidence = inverse of volatility.
        (We keep the original .confidence field for backward compatibility.)
        """
        v = self.volatility
        return max(0.0, 1.0 - min(v, 1.0))

    def as_dict(self) -> Dict[str, float]:
        return {
            "joy": self.joy,
            "calm": self.calm,
            "focus": self.focus,
            "tension": self.tension,
            "curiosity": self.curiosity,
            "fatigue": self.fatigue,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "EmotionalState":
        return cls(
            joy=data.get("joy", 0.5),
            calm=data.get("calm", 0.5),
            focus=data.get("focus", 0.5),
            tension=data.get("tension", 0.5),
            curiosity=data.get("curiosity", 0.5),
            fatigue=data.get("fatigue", 0.0),
            confidence=data.get("confidence", 0.5),
        )


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def update_emotional_state(
    state: EmotionalState,
    delta: Dict[str, float],
    inertia: float = 0.7,
    decay_rate: float = 0.05,
) -> EmotionalState:
    """
    Core emotional state update:
    - apply delta
    - apply inertia
    - apply decay
    - clamp to [0, 1]
    - store previous state for volatility computation
    """
    current = state.as_dict()
    new_state: Dict[str, float] = {}

    for key, old_value in current.items():
        d = delta.get(key, 0.0)

        # apply inertia: blend old state and delta
        blended = (old_value * inertia) + (d * (1.0 - inertia))

        # apply decay: gentle pull toward baseline (0.5 for most, 0.0 for fatigue)
        baseline = 0.5 if key != "fatigue" else 0.0
        decayed = blended + (baseline - blended) * decay_rate

        new_state[key] = clamp(decayed)

    updated = EmotionalState.from_dict(new_state)

    # ⭐ store previous state for volatility calculation
    updated._prev_state = state

    return updated