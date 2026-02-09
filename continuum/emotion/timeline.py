# continuum/emotion/timeline.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

@dataclass
class ArcPoint:
    timestamp: datetime
    emotion: str
    intensity: float

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "emotion": self.emotion,
            "intensity": self.intensity,
        }
    
@dataclass
class EmotionalArcTimeline:
    window_minutes: int = 30
    points: List[ArcPoint] = field(default_factory=list)

    def add_point(self, emotion: str, intensity: float):
        """Record a new emotional point in the timeline."""
        self.points.append(
            ArcPoint(
                timestamp=datetime.now(),
                emotion=emotion,
                intensity=intensity
            )
        )
        self.trim()

    def trim(self):
        """Keep only points within the rolling time window."""
        cutoff = datetime.now() - timedelta(minutes=self.window_minutes)
        self.points = [p for p in self.points if p.timestamp >= cutoff]

    def get_recent(self, n: int = 10) -> List[ArcPoint]:
        """Return the last N emotional points."""
        return self.points[-n:]

    def get_sparkline_data(self):
        """Return simplified data for sparkline visualization."""
        return [(p.timestamp, p.intensity) for p in self.points]

    def get_emotion_distribution(self):
        """Return a count of emotions in the current window."""
        dist = {}
        for p in self.points:
            dist[p.emotion] = dist.get(p.emotion, 0) + 1
        return dist

    def get_momentum(self) -> Optional[float]:
        """Return emotional momentum: positive = rising intensity, negative = falling."""
        if len(self.points) < 2:
            return None
        return self.points[-1].intensity - self.points[-2].intensity

    def get_current(self) -> Optional[ArcPoint]:
        """Return the most recent emotional point."""
        return self.points[-1] if self.points else None