# continuum/emotion/emotional_arc_engine.py

from typing import Any, Dict, List
from .state_machine import EmotionalState


class EmotionalArcEngine:
    """
    Tracks emotional arc history and provides arc classification.
    """

    def __init__(self, max_history: int = 50) -> None:
        self.history: List[Dict[str, Any]] = []
        self.max_history = max_history

    def record_snapshot(
        self,
        emotional_state: EmotionalState,
        dominant_emotion: str,
        fusion_weights: Dict[str, float] | None,
    ) -> None:
        snapshot = {
            "turn": len(self.history),
            "state": emotional_state.as_dict(),
            "dominant": dominant_emotion,
            "volatility": emotional_state.volatility,
            "confidence": emotional_state.confidence,
            "fusion_weights": fusion_weights or {},
        }
        self.history.append(snapshot)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history

    def _slope(self, key: str, window: int = 3) -> float:
        if len(self.history) < window:
            return 0.0
        start = self.history[-window]["state"].get(key, 0.0)
        end = self.history[-1]["state"].get(key, 0.0)
        return end - start

    def classify_arc(self) -> str:
        if len(self.history) < 3:
            return "Insufficient data for arc classification"

        curiosity_s = self._slope("curiosity")
        tension_s = self._slope("tension")
        calm_s = self._slope("calm")

        if curiosity_s > 0.15:
            return "Rising Curiosity Arc"
        if tension_s > 0.15:
            return "Rising Tension Arc"
        if calm_s > 0.15:
            return "Settling Calm Arc"
        if tension_s < -0.15:
            return "Tension-Recovery Arc"

        return "Stable Emotional Arc"