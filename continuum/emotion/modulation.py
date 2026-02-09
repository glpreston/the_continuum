#continuum/emotion/modulation.py
# ============================================================
# Emotional Modulation Constants (Phase‑5)
# ============================================================

WARMTH_SOFT_MULT = 0.3
SOFTNESS_SOFT_MULT = 0.25

WARMTH_BRIGHT_MULT = 0.15
CREATIVITY_BRIGHT_MULT = 0.2

MEMORY_WARMTH_MULT = 0.2
MEMORY_COHESION_MULT = 0.15

CLARITY_SUPPORTIVE_MULT = 1.05
CLARITY_CONF_LOW_MULT = 0.95
SOFTNESS_CONF_LOW_MULT = 1.1
CLARITY_CONF_HIGH_MULT = 1.1
STRUCTURE_CONF_HIGH_MULT = 1.1

BREVITY_EXPRESSIVE_MULT = 0.9
BREVITY_SOFT_MULT = 1.1

NARRATIVE_MEMORY_MULT = 1.1

# ============================================================

from dataclasses import dataclass
from continuum.core.logger import log_debug
from .state import EmotionalState


@dataclass
class OutputModulationEngine:
    state: EmotionalState

    def modulate(self, text: str, style_weights: dict) -> str:
        """Apply emotional modulation to the rewritten text."""

        emotion = self.state.current_emotion
        intensity = self.state.intensity
        volatility = self.state.volatility
        confidence = self.state.confidence
        memory = self.state.memory_influence
        mode = self.state.mode

        log_debug(
            f"[AIRA][emotion_modulation] Starting modulation: "
            f"emotion={emotion}, intensity={intensity:.2f}, "
            f"volatility={volatility:.2f}, confidence={confidence:.2f}, "
            f"memory={memory:.2f}, mode={mode}"
        )

        w = style_weights.copy()

        # Warmth & softness
        if emotion in ["soft", "calming"]:
            w["warmth"] *= 1.0 + (WARMTH_SOFT_MULT * intensity)
            w["softness"] *= 1.0 + (SOFTNESS_SOFT_MULT * intensity)

        if emotion == "bright":
            w["warmth"] *= 1.0 + (WARMTH_BRIGHT_MULT * intensity)
            w["creativity"] *= 1.0 + (CREATIVITY_BRIGHT_MULT * intensity)

        if memory > 0.2:
            w["warmth"] *= 1.0 + (MEMORY_WARMTH_MULT * memory)
            w["cohesion"] *= 1.0 + (MEMORY_COHESION_MULT * memory)

        # Clarity vs softness
        if mode == "exploratory":
            w["clarity"] *= 0.9
            w["creativity"] *= 1.0 + (0.3 * intensity)

        if mode in ["grounding", "supportive"]:
            w["clarity"] *= CLARITY_SUPPORTIVE_MULT

        if confidence < 0.4:
            w["clarity"] *= CLARITY_CONF_LOW_MULT
            w["softness"] *= SOFTNESS_CONF_LOW_MULT
        elif confidence > 0.7:
            w["clarity"] *= CLARITY_CONF_HIGH_MULT
            w["structure"] *= STRUCTURE_CONF_HIGH_MULT

        # Conciseness vs expressiveness
        if emotion in ["bright", "exploratory"]:
            w["brevity"] *= BREVITY_EXPRESSIVE_MULT
        elif emotion in ["soft", "calming"]:
            w["brevity"] *= BREVITY_SOFT_MULT

        if memory > 0.3:
            w["narrative"] *= NARRATIVE_MEMORY_MULT

        # Rhythm modulation
        if emotion == "soft":
            text = self._smooth_rhythm(text, volatility)
        if emotion == "bright":
            text = self._energize_rhythm(text, volatility)
        if emotion == "calming":
            text = self._slow_rhythm(text, volatility)

        log_debug(
            f"[AIRA][emotion_modulation] Weights applied: {w}"
        )

        return self._apply_weights(text, w)

    def _smooth_rhythm(self, text: str, volatility: float) -> str:
        if volatility > 0.6:
            return text.replace(".", "...").replace("!", ".")
        return text.replace(".", "..").replace("!", ".")

    def _energize_rhythm(self, text: str, volatility: float) -> str:
        if volatility < 0.4:
            return text.replace("...", ".").replace(".", "! ")
        return text.replace("...", ".").replace(".", ". ")

    def _slow_rhythm(self, text: str, volatility: float) -> str:
        text = text.replace("!", ".").replace("...", "..")
        if volatility > 0.6:
            text = text.replace(".", "..")
        return text

    def _apply_weights(self, text: str, w: dict) -> str:
        log_debug(
            f"[AIRA][emotion_modulation] Final modulation complete."
        )
        return text