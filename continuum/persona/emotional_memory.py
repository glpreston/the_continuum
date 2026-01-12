# continuum/persona/emotional_memory.py

from collections import deque

class EmotionalMemory:
    """
    Tracks recent emotional context over the conversation.
    Stores rolling emotion_label + intensity events and exposes
    a smoothed emotional state for downstream systems.
    """

    def __init__(self, max_events: int = 20):
        self.max_events = max_events
        self.events = deque(maxlen=max_events)

    def add_event(self, emotion_label: str, intensity: float):
        """
        Store a simple emotional event.
        """
        if not emotion_label:
            return

        self.events.append({
            "emotion_label": emotion_label,
            "intensity": intensity
        })

    def is_empty(self) -> bool:
        return len(self.events) == 0

    def get_last_emotion(self) -> str:
        """
        Return the most recent detected emotion label, or empty string.
        """
        if not self.events:
            return ""
        return self.events[-1]["emotion_label"]

    def get_smoothed_emotion(self) -> str:
        """
        Weighted smoothing over the last 10 emotional events.
        Most recent events have higher weight.
        """
        if not self.events:
            return ""

        # Convert deque → list so slicing works
        recent = list(self.events)[-10:]
        recent = list(reversed(recent))  # newest first

        weights = []
        emotions = []

        for i, event in enumerate(recent):
            weight = 1.0 / (i + 1)  # 1.0, 0.5, 0.33...
            weights.append(weight)
            emotions.append((event["emotion_label"], event["intensity"]))

        # Aggregate weighted scores
        scores = {}
        for (label, intensity), w in zip(emotions, weights):
            scores[label] = scores.get(label, 0) + intensity * w

        if not scores:
            return ""

        return max(scores, key=scores.get)

    def get_emotional_state(self) -> str:
        """
        Returns the best emotional summary for downstream systems.
        """
        smoothed = self.get_smoothed_emotion()
        if smoothed:
            return smoothed
        return self.get_last_emotion()

    def get_smoothed_state(self):
        """
        Backwards‑compatible method for the UI.
        Supports both old-style events (sentiment + emotions dict)
        and new-style events (emotion_label + intensity).
        """

        if not self.events:
            return {
                "avg_sentiment": 0.0,
                "avg_emotions": {},
            }

        # If events use the NEW format (emotion_label + intensity)
        if "emotion_label" in self.events[0]:
            # Convert new format into old-style aggregates
            avg_sentiment = sum(e["intensity"] for e in self.events) / len(self.events)

            emotion_sums = {}
            for e in self.events:
                label = e["emotion_label"]
                emotion_sums[label] = emotion_sums.get(label, 0.0) + e["intensity"]

            avg_emotions = {k: v / len(self.events) for k, v in emotion_sums.items()}

            return {
                "avg_sentiment": avg_sentiment,
                "avg_emotions": avg_emotions,
            }

        # Otherwise fall back to OLD format
        avg_sentiment = sum(e["sentiment"] for e in self.events) / len(self.events)

        emotion_sums = {}
        for e in self.events:
            for k, v in e["emotions"].items():
                emotion_sums[k] = emotion_sums.get(k, 0.0) + v

        avg_emotions = {k: v / len(self.events) for k, v in emotion_sums.items()}

        return {
            "avg_sentiment": avg_sentiment,
            "avg_emotions": avg_emotions,
        }