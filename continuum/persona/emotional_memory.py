#  continuum/persona/emotional_memory.py

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from math import sqrt
from continuum.emotion.emotional_memory_decay import update_emotional_memory
import datetime


# ---------------------------------------------------------------------------
# EI‑2.0 Emotional Event
# ---------------------------------------------------------------------------

@dataclass
class EmotionalEvent:
    """
    EI‑2.0 emotional memory event.

    - timestamp: ISO 8601 string
    - raw_state: dict of EI‑2.0 emotion dimensions -> float
    - dominant_emotion: label for the dominant emotion at this moment
    - metadata: optional contextual info (speaker, turn_id, source, etc.)
    """
    timestamp: str
    raw_state: Dict[str, float]
    dominant_emotion: str
    metadata: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# EI‑2.0 Emotional Memory
# ---------------------------------------------------------------------------

class EmotionalMemory:
    """
    EI‑2.0 EmotionalMemory

    Tracks:
    - short_term_emotion: most recent dominant emotion
    - long_term_emotion: dominant emotion derived from smoothed state
    - smoothed_state: exponentially smoothed EI‑2.0 dimensions
    - volatility: magnitude of recent emotional change
    - confidence: inverse of volatility, normalized
    - events: rolling list of EmotionalEvent objects
    """

    def __init__(
        self,
        smoothing_factor: float = 0.3,
        max_events: int = 200,
        min_confidence: float = 0.0,
        max_confidence: float = 1.0,
        volatility_normalization: float = 5.0,
    ) -> None:

        self.smoothing_factor = smoothing_factor
        self.max_events = max_events
        self.min_confidence = min_confidence
        self.max_confidence = max_confidence
        self.volatility_normalization = volatility_normalization

        self.events: List[EmotionalEvent] = []
        self.smoothed_state: Dict[str, float] = {}
        self.previous_smoothed_state: Optional[Dict[str, float]] = None

        self.short_term_emotion: Optional[str] = None
        self.long_term_emotion: Optional[str] = None
        self.volatility: float = 0.0
        self.confidence: float = max_confidence

        # Step F‑3: Track last update time for decay
        self.last_update_ts = datetime.datetime.utcnow().timestamp()

    # -----------------------------------------------------------------------
    # Core update pipeline
    # -----------------------------------------------------------------------

    def add_event(
        self,
        raw_state: Dict[str, float],
        dominant_emotion: str,
        timestamp: Optional[datetime.datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:

        if timestamp is None:
            timestamp = datetime.datetime.utcnow()

        event = EmotionalEvent(
            timestamp=timestamp.isoformat(),
            raw_state=dict(raw_state),
            dominant_emotion=dominant_emotion,
            metadata=metadata or {},
        )

        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events.pop(0)

        self.short_term_emotion = dominant_emotion

        # Update smoothed state + metrics
        self._update_smoothed_state(raw_state)
        self._update_volatility()
        self._update_confidence()
        self._update_long_term_emotion()

        # Step F‑3: Apply emotional decay + recovery
        self._apply_decay_and_recovery()

        # Update timestamp
        self.last_update_ts = datetime.datetime.utcnow().timestamp()

    # -----------------------------------------------------------------------
    # Step F‑3: Emotional Decay + Recovery
    # -----------------------------------------------------------------------

    def _apply_decay_and_recovery(self):
        """
        Applies exponential decay + gentle recovery to the smoothed emotional state.
        This keeps emotional memory realistic and prevents long-term buildup.
        """
        if not self.smoothed_state:
            return

        # Convert smoothed_state to a simple dict for decay module
        decayed = update_emotional_memory(
            memory_state=self.smoothed_state,
            last_update_ts=self.last_update_ts,
            half_life_seconds=180.0,   # 3-minute half-life
            recovery_rate=0.02         # gentle recovery
        )

        self.smoothed_state = decayed

    # -----------------------------------------------------------------------
    # Smoothing
    # -----------------------------------------------------------------------

    def _update_smoothed_state(self, raw_state: Dict[str, float]) -> None:
        alpha = self.smoothing_factor

        if not self.smoothed_state:
            self.smoothed_state = dict(raw_state)
            self.previous_smoothed_state = None
            return

        self.previous_smoothed_state = dict(self.smoothed_state)

        for dim, value in raw_state.items():
            prev = self.smoothed_state.get(dim, value)
            self.smoothed_state[dim] = alpha * value + (1.0 - alpha) * prev

        # Decay missing dimensions
        for dim in list(self.smoothed_state.keys()):
            if dim not in raw_state:
                prev = self.smoothed_state[dim]
                self.smoothed_state[dim] = (1.0 - alpha) * prev

    # -----------------------------------------------------------------------
    # Volatility + Confidence
    # -----------------------------------------------------------------------

    def _update_volatility(self) -> None:
        if self.previous_smoothed_state is None:
            self.volatility = 0.0
            return

        dims = set(self.smoothed_state.keys()) | set(self.previous_smoothed_state.keys())
        squared_sum = 0.0

        for dim in dims:
            current = self.smoothed_state.get(dim, 0.0)
            previous = self.previous_smoothed_state.get(dim, 0.0)
            diff = current - previous
            squared_sum += diff * diff

        self.volatility = sqrt(squared_sum)

    def _update_confidence(self) -> None:
        if self.volatility_normalization <= 0:
            self.confidence = self.max_confidence
            return

        normalized_vol = self.volatility / self.volatility_normalization
        base_conf = 1.0 / (1.0 + normalized_vol)

        span = self.max_confidence - self.min_confidence
        self.confidence = self.min_confidence + span * base_conf

    # -----------------------------------------------------------------------
    # Long-term emotion
    # -----------------------------------------------------------------------

    def _update_long_term_emotion(self) -> None:
        if not self.smoothed_state:
            self.long_term_emotion = None
            return

        self.long_term_emotion = max(self.smoothed_state.items(), key=lambda kv: kv[1])[0]

    # -----------------------------------------------------------------------
    # Debug payload
    # -----------------------------------------------------------------------

    def get_debug_payload(self, last_n: int = 5) -> Dict[str, Any]:
        last_events = self.events[-last_n:]
        trend = self._compute_trend()

        return {
            "last_events": [asdict(e) for e in last_events],
            "smoothed_state": dict(self.smoothed_state),
            "volatility": self.volatility,
            "confidence": self.confidence,
            "short_term_emotion": self.short_term_emotion,
            "long_term_emotion": self.long_term_emotion,
            "trend": trend,
        }

    def _compute_trend(self) -> Dict[str, str]:
        if self.previous_smoothed_state is None:
            return {dim: "stable" for dim in self.smoothed_state.keys()}

        trend: Dict[str, str] = {}
        dims = set(self.smoothed_state.keys()) | set(self.previous_smoothed_state.keys())

        for dim in dims:
            current = self.smoothed_state.get(dim, 0.0)
            previous = self.previous_smoothed_state.get(dim, 0.0)
            diff = current - previous

            if abs(diff) < 1e-6:
                trend[dim] = "stable"
            elif diff > 0:
                trend[dim] = "rising"
            else:
                trend[dim] = "falling"

        return trend

    # -----------------------------------------------------------------------
    # Legacy migration (EI‑1.0 → EI‑2.0)
    # -----------------------------------------------------------------------

    @classmethod
    def from_legacy(
        cls,
        legacy_data: Dict[str, Any],
        mapping_fn: Optional[Any] = None,
        **kwargs: Any,
    ) -> "EmotionalMemory":

        memory = cls(**kwargs)
        events = legacy_data.get("events", [])

        for legacy_event in events:
            if mapping_fn is not None:
                raw_state, dominant_emotion = mapping_fn(legacy_event)
            else:
                legacy_emotions = legacy_event.get("emotions", {})
                raw_state = dict(legacy_emotions)
                dominant_emotion = (
                    max(legacy_emotions.items(), key=lambda kv: kv[1])[0]
                    if legacy_emotions else "neutral"
                )

            ts_raw = legacy_event.get("timestamp")
            if isinstance(ts_raw, str):
                try:
                    ts = datetime.datetime.fromisoformat(ts_raw)
                except Exception:
                    ts = datetime.datetime.utcnow()
            elif isinstance(ts_raw, datetime.datetime):
                ts = ts_raw
            else:
                ts = datetime.datetime.utcnow()

            metadata = legacy_event.get("metadata", {})
            memory.add_event(raw_state=raw_state, dominant_emotion=dominant_emotion, timestamp=ts, metadata=metadata)

        return memory

    # -----------------------------------------------------------------------
    # Backwards‑compatible UI method
    # -----------------------------------------------------------------------

    def get_smoothed_state(self) -> Dict[str, Any]:
        """
        Backwards‑compatible method for the UI.
        Returns EI‑2.0 smoothed state in a stable structure.
        """
        return {
            "smoothed_state": dict(self.smoothed_state),
            "dominant_emotion": self.long_term_emotion,
            "confidence": self.confidence,
            "volatility": self.volatility,
        }