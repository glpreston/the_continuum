from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
from .state import EmotionalState
from .timeline import ArcPoint

@dataclass
class EmotionalMemoryEngine:
    state: EmotionalState
    short_term_limit: int = 10

    # Short-term memory: last N emotional states
    short_term: List[ArcPoint] = field(default_factory=list)

    # Long-term memory: aggregated emotional tendencies
    long_term: Dict[str, float] = field(default_factory=lambda: {
        "soft": 0.0,
        "bright": 0.0,
        "calming": 0.0,
        "exploratory": 0.0,
        "balanced": 0.0
    })

    def update(self, point: ArcPoint):
        """
        Update both short-term and long-term emotional memory.
        """

        # -----------------------------
        # 1. Update short-term memory
        # -----------------------------
        self.short_term.append(point)
        if len(self.short_term) > self.short_term_limit:
            self.short_term.pop(0)

        # -----------------------------
        # 2. Update long-term memory
        # -----------------------------
        if point.emotion in self.long_term:
            self.long_term[point.emotion] += point.intensity

        # Normalize long-term memory occasionally
        self._normalize_long_term()

    def _normalize_long_term(self):
        total = sum(self.long_term.values())
        if total == 0:
            return
        for k in self.long_term:
            self.long_term[k] /= total

    # ---------------------------------------------------------
    # Emotional Influence Functions
    # ---------------------------------------------------------

    def get_lingering_mood(self):
        """
        Returns the dominant emotion in short-term memory.
        """
        if not self.short_term:
            return None

        counts = {}
        for p in self.short_term:
            counts[p.emotion] = counts.get(p.emotion, 0) + p.intensity

        return max(counts, key=counts.get)

    def get_long_term_bias(self):
        """
        Returns the emotion Aira tends to drift toward over time.
        """
        if not self.long_term:
            return None
        return max(self.long_term, key=self.long_term.get)

    def apply_memory_influence(self):
        """
        Adjust emotional state based on memory.
        """

        lingering = self.get_lingering_mood()
        bias = self.get_long_term_bias()

        # Slight nudge toward lingering mood
        if lingering and lingering != self.state.current_emotion:
            self.state.intensity *= 0.95

        # Very slight nudge toward long-term bias
        if bias and bias != self.state.current_emotion:
            self.state.intensity *= 0.98