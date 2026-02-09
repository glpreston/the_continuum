# continuum/emotion/state.py
# ============================================================
# Emotional Engine Constants (Phase‑5)
# ============================================================

DEFAULT_INTENSITY = 0.3
DEFAULT_VOLATILITY = 0.5
DEFAULT_DECAY_RATE = 0.1

ARC_ADVANCE_RATE = 0.02

CONFIDENCE_DECAY = 0.98
CONFIDENCE_STABILITY_GAIN = 0.05

# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from continuum.core.logger import log_debug
@dataclass
class EmotionalSnapshot:
    timestamp: datetime
    emotion: str
    intensity: float
    mode: str
    confidence: float
    memory_influence: float
    arc_position: float


@dataclass
class EmotionalState:
    # Core emotional fields
    baseline: str = "balanced"
    current_emotion: str = "balanced"
    intensity: float = DEFAULT_INTENSITY
    volatility: float = DEFAULT_VOLATILITY
    decay_rate: float = DEFAULT_DECAY_RATE

    # EI‑2.0 extensions
    mode: str = "neutral"
    confidence: float = 0.5
    memory_influence: float = 0.0
    arc_position: float = 0.0

    # History / context
    trajectory: List[EmotionalSnapshot] = field(default_factory=list)
    last_user_emotion: Optional[str] = None
    last_transition_time: Optional[datetime] = None

    def record(self):
        """Save current emotional state to trajectory."""
        snapshot = EmotionalSnapshot(
            timestamp=datetime.now(),
            emotion=self.current_emotion,
            intensity=self.intensity,
            mode=self.mode,
            confidence=self.confidence,
            memory_influence=self.memory_influence,
            arc_position=self.arc_position,
        )
        self.trajectory.append(snapshot)

        log_debug(
            f"[AIRA][emotion_state] Recorded snapshot: "
            f"emotion={self.current_emotion}, intensity={self.intensity:.2f}, "
            f"mode={self.mode}, confidence={self.confidence:.2f}, "
            f"memory={self.memory_influence:.2f}, arc={self.arc_position:.2f}"
        )

    def decay(self):
        """Move emotion back toward baseline over time."""
        if self.current_emotion != self.baseline:
            self.intensity -= self.decay_rate
            if self.intensity <= 0.1:
                self.current_emotion = self.baseline
                self.intensity = 0.1
                self.mode = "neutral"
                self.memory_influence *= 0.8

        # Stabilize volatility and confidence
        self.volatility = max(0.1, self.volatility * 0.97)
        self.confidence = min(1.0, self.confidence * 1.01)

        # Advance arc
        self.arc_position = min(1.0, self.arc_position + ARC_ADVANCE_RATE)

        log_debug(
            f"[AIRA][emotion_state] Decay applied: "
            f"emotion={self.current_emotion}, intensity={self.intensity:.2f}, "
            f"volatility={self.volatility:.2f}, confidence={self.confidence:.2f}, "
            f"arc={self.arc_position:.2f}"
        )

    def apply_user_emotion(self, user_emotion: str):
        """Shift emotional state based on user emotion."""
        self.last_user_emotion = user_emotion
        self.last_transition_time = datetime.now()

        if user_emotion == "frustrated":
            self.current_emotion = "calming"
            self.mode = "grounding"
            self.intensity = min(1.0, self.intensity + 0.2)
            self.confidence = max(0.4, self.confidence - 0.1)
            self.volatility = min(1.0, self.volatility + 0.1)

        elif user_emotion == "sad":
            self.current_emotion = "soft"
            self.mode = "supportive"
            self.intensity = min(1.0, self.intensity + 0.15)
            self.confidence = max(0.4, self.confidence - 0.05)

        elif user_emotion == "excited":
            self.current_emotion = "bright"
            self.mode = "celebratory"
            self.intensity = min(1.0, self.intensity + 0.25)
            self.confidence = min(1.0, self.confidence + 0.15)
            self.volatility = min(1.0, self.volatility + 0.1)

        elif user_emotion == "curious":
            self.current_emotion = "exploratory"
            self.mode = "exploratory"
            self.intensity = min(1.0, self.intensity + 0.1)
            self.confidence = min(1.0, self.confidence + 0.1)

        else:
            self.current_emotion = self.baseline
            self.mode = "neutral"
            self.intensity = max(0.2, self.intensity * 0.95)

        self.arc_position = 0.0

        log_debug(
            f"[AIRA][emotion_state] User emotion applied '{user_emotion}': "
            f"emotion={self.current_emotion}, intensity={self.intensity:.2f}, "
            f"mode={self.mode}, confidence={self.confidence:.2f}, "
            f"volatility={self.volatility:.2f}"
        )

        self.record()