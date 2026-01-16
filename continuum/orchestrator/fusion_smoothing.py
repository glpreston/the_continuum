# continuum/orchestrator/fusion_smoothing.py

from typing import Dict, Optional


class FusionSmoother:
    """
    Exponential moving average smoother for fusion weights.
    """

    def __init__(self, alpha: float = 0.6) -> None:
        self.alpha = alpha
        self.prev_weights: Optional[Dict[str, float]] = None

    def smooth(self, current: Dict[str, float] | None) -> Dict[str, float] | None:
        if current is None:
            return None

        if self.prev_weights is None:
            self.prev_weights = current
            return current

        smoothed: Dict[str, float] = {}
        for actor, weight in current.items():
            prev = self.prev_weights.get(actor, weight)
            smoothed[actor] = (self.alpha * weight) + ((1 - self.alpha) * prev)

        self.prev_weights = smoothed
        return smoothed