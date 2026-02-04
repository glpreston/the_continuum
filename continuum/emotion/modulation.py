from dataclasses import dataclass
from .state import EmotionalState

@dataclass
class OutputModulationEngine:
    state: EmotionalState

    def modulate(self, text: str, style_weights: dict) -> str:
        """
        Apply emotional modulation to the rewritten text.
        This adjusts tone, warmth, clarity, rhythm, and metaphor density.
        """

        emotion = self.state.current_emotion
        intensity = self.state.intensity

        # Clone weights so we don't mutate the persona
        w = style_weights.copy()

        # ---------------------------------------------------------
        # 1. Warmth modulation
        # ---------------------------------------------------------
        if emotion in ["soft", "calming"]:
            w["warmth"] *= 1.0 + (0.3 * intensity)
            w["softness"] *= 1.0 + (0.25 * intensity)

        if emotion == "bright":
            w["warmth"] *= 1.0 + (0.15 * intensity)
            w["creativity"] *= 1.0 + (0.2 * intensity)

        # ---------------------------------------------------------
        # 2. Clarity modulation
        # ---------------------------------------------------------
        if emotion == "exploratory":
            w["clarity"] *= 0.9
            w["creativity"] *= 1.0 + (0.3 * intensity)

        if emotion == "calming":
            w["clarity"] *= 1.1

        # ---------------------------------------------------------
        # 3. Conciseness vs expressiveness
        # ---------------------------------------------------------
        if emotion in ["bright", "exploratory"]:
            w["brevity"] *= 0.9  # more expressive
        elif emotion in ["soft", "calming"]:
            w["brevity"] *= 1.1  # more concise, gentle

        # ---------------------------------------------------------
        # 4. Rhythm modulation
        # ---------------------------------------------------------
        if emotion == "soft":
            text = self._smooth_rhythm(text)

        if emotion == "bright":
            text = self._energize_rhythm(text)

        if emotion == "calming":
            text = self._slow_rhythm(text)

        # ---------------------------------------------------------
        # 5. Apply weighted style adjustments
        # ---------------------------------------------------------
        text = self._apply_weights(text, w)

        return text

    # -------------------------------------------------------------
    # Rhythm helpers
    # -------------------------------------------------------------

    def _smooth_rhythm(self, text: str) -> str:
        """Softens rhythm: longer sentences, gentle transitions."""
        return text.replace(".", "...").replace("!", ".")

    def _energize_rhythm(self, text: str) -> str:
        """Brightens rhythm: shorter sentences, more punch."""
        return text.replace("...", ".").replace(".", "! ")

    def _slow_rhythm(self, text: str) -> str:
        """Calming rhythm: reduce intensity, soften punctuation."""
        return text.replace("!", ".").replace("...", "..")

    # -------------------------------------------------------------
    # Style weight application
    # -------------------------------------------------------------

    def _apply_weights(self, text: str, w: dict) -> str:
        """
        Placeholder for deeper style integration.
        This will eventually hook into your apply_style() engine.
        """
        # For now, we simply return the text.
        # Later, we will integrate weights into the rewrite pipeline.
        return text