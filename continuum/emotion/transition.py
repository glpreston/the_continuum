from datetime import datetime
from .state import EmotionalState
from .timeline import EmotionalArcTimeline

class EmotionalTransitionEngine:

    # Persona-specific emotional influence map
    EMOTION_MAP = {
        "frustrated": "calming",
        "sad": "soft",
        "excited": "bright",
        "curious": "exploratory",
        "neutral": None
    }

    def __init__(self, state: EmotionalState, timeline: EmotionalArcTimeline):
        self.state = state
        self.timeline = timeline

    def apply_user_emotion(self, user_emotion: str, strength: float = 0.5):
        """
        Main entry point: update emotional state based on user emotion.
        Strength = 0–1 indicating how strong the user's emotion is.
        """

        # 1. Determine target emotion
        target = self.EMOTION_MAP.get(user_emotion, None)

        if target is None:
            # Neutral or unknown emotion → decay toward baseline
            self.state.decay()
            self.timeline.add_point(self.state.current_emotion, self.state.intensity)
            return

        # 2. Apply volatility (how fast Aira shifts)
        shift_speed = self.state.volatility * strength

        # 3. Update emotion
        self.state.current_emotion = target

        # 4. Update intensity
        self.state.intensity = min(1.0, self.state.intensity + shift_speed)

        # 5. Record transition
        self.state.last_user_emotion = user_emotion
        self.state.last_transition_time = datetime.now()

        # 6. Add to timeline
        self.timeline.add_point(self.state.current_emotion, self.state.intensity)

    def stabilize(self):
        """
        Called periodically to reduce oscillation and drift.
        """
        momentum = self.timeline.get_momentum()

        # If momentum is None or small, do nothing
        if momentum is None or abs(momentum) < 0.05:
            return

        # If intensity is rising too fast → dampen
        if momentum > 0.1:
            self.state.intensity = max(0.1, self.state.intensity - 0.05)

        # If intensity is falling too fast → soften decay
        if momentum < -0.1:
            self.state.intensity = min(1.0, self.state.intensity + 0.05)

        # Re-record after stabilization
        self.timeline.add_point(self.state.current_emotion, self.state.intensity)