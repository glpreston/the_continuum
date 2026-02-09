#continuum/emotion/memory.py
# ============================================================
# Emotional Memory Constants (Phase‑5)
# ============================================================

SHORT_TERM_LIMIT = 10

MEMORY_INFLUENCE_GROWTH = 0.05
MEMORY_INFLUENCE_DECAY = 0.9

LINGERING_VOLATILITY_REDUCTION = 0.9

LONG_TERM_INTENSITY_DECAY = 0.98

# ============================================================

from dataclasses import dataclass, field
from typing import List, Dict
from continuum.core.logger import log_debug
from .state import EmotionalState
from .timeline import ArcPoint


@dataclass
class EmotionalMemoryEngine:
    state: EmotionalState
    short_term_limit: int = SHORT_TERM_LIMIT

    short_term: List[ArcPoint] = field(default_factory=list)

    long_term: Dict[str, float] = field(default_factory=lambda: {
        "soft": 0.0,
        "bright": 0.0,
        "calming": 0.0,
        "exploratory": 0.0,
        "balanced": 0.0,
    })

    def update(self, point: ArcPoint):
        """Update short-term and long-term emotional memory."""

        # Short-term memory
        self.short_term.append(point)
        if len(self.short_term) > self.short_term_limit:
            self.short_term.pop(0)

        log_debug(
            f"[AIRA][emotion_memory] Short-term updated: "
            f"emotion={point.emotion}, intensity={point.intensity:.2f}"
        )

        # Long-term memory
        if point.emotion in self.long_term:
            self.long_term[point.emotion] += point.intensity

        self._normalize_long_term()

        # Apply memory influence to emotional state
        self.apply_memory_influence()

    def _normalize_long_term(self):
        total = sum(self.long_term.values())
        if total == 0:
            return

        for k in self.long_term:
            self.long_term[k] /= total

        log_debug(
            f"[AIRA][emotion_memory] Long-term normalized: {self.long_term}"
        )

    def get_lingering_mood(self):
        if not self.short_term:
            return None

        counts: Dict[str, float] = {}
        for p in self.short_term:
            counts[p.emotion] = counts.get(p.emotion, 0.0) + p.intensity

        return max(counts, key=counts.get)

    def get_long_term_bias(self):
        if not self.long_term:
            return None
        return max(self.long_term, key=self.long_term.get)

    def apply_memory_influence(self):
        lingering = self.get_lingering_mood()
        bias = self.get_long_term_bias()

        # Memory influence growth/decay
        if lingering:
            self.state.memory_influence = min(
                1.0, self.state.memory_influence + MEMORY_INFLUENCE_GROWTH
            )
        else:
            self.state.memory_influence = max(
                0.0, self.state.memory_influence * MEMORY_INFLUENCE_DECAY
            )

        # Lingering mood shaping
        if lingering and lingering != self.state.current_emotion:
            self.state.intensity *= 0.95
            if lingering in ["soft", "calming"]:
                self.state.volatility = max(
                    0.1, self.state.volatility * LINGERING_VOLATILITY_REDUCTION
                )

        # Long-term bias shaping
        if bias and bias != self.state.current_emotion:
            self.state.intensity *= LONG_TERM_INTENSITY_DECAY

        # Confidence shaped by stability
        stability = 1.0 - self.state.volatility
        self.state.confidence = max(
            0.2,
            min(1.0, self.state.confidence * 0.98 + stability * 0.05),
        )

        log_debug(
            f"[AIRA][emotion_memory] Memory influence applied: "
            f"lingering={lingering}, bias={bias}, "
            f"memory={self.state.memory_influence:.2f}, "
            f"confidence={self.state.confidence:.2f}, "
            f"volatility={self.state.volatility:.2f}"
        )