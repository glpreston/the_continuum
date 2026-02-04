from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict

@dataclass
class EmotionalSnapshot:
    timestamp: datetime
    emotion: str
    intensity: float

@dataclass
class EmotionalState:
    baseline: str = "balanced"
    current_emotion: str = "balanced"
    intensity: float = 0.3  # 0–1
    volatility: float = 0.5
    decay_rate: float = 0.1

    trajectory: List[EmotionalSnapshot] = field(default_factory=list)
    last_user_emotion: str = None
    last_transition_time: datetime = None

    def record(self):
        """Save current emotional state to trajectory."""
        self.trajectory.append(
            EmotionalSnapshot(
                timestamp=datetime.now(),
                emotion=self.current_emotion,
                intensity=self.intensity
            )
        )

    def decay(self):
        """Move emotion back toward baseline over time."""
        if self.current_emotion != self.baseline:
            self.intensity -= self.decay_rate
            if self.intensity <= 0.1:
                self.current_emotion = self.baseline
                self.intensity = 0.1

    def apply_user_emotion(self, user_emotion: str):
        """Shift emotional state based on user emotion."""
        self.last_user_emotion = user_emotion
        self.last_transition_time = datetime.now()

        # Simple placeholder rule — replaced in D3
        if user_emotion == "frustrated":
            self.current_emotion = "calming"
            self.intensity = min(1.0, self.intensity + 0.2)

        elif user_emotion == "sad":
            self.current_emotion = "soft"
            self.intensity = min(1.0, self.intensity + 0.15)

        elif user_emotion == "excited":
            self.current_emotion = "bright"
            self.intensity = min(1.0, self.intensity + 0.25)

        elif user_emotion == "curious":
            self.current_emotion = "exploratory"
            self.intensity = min(1.0, self.intensity + 0.1)

        self.record()