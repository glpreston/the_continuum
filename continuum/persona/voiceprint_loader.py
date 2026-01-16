# continuum/persona/voiceprint_loader.py

"""
Continuum Voiceprint Loader
Provides a clean API for accessing the Unified Continuum Voiceprint Specification.
"""

from typing import Dict, Any
from .voiceprints import SYSTEM_VOICEPRINT


class VoiceprintLoader:
    """Loads and exposes the Continuum Unified Voiceprint."""

    def __init__(self):
        self.voiceprint = SYSTEM_VOICEPRINT

    # -----------------------------------------------------
    # Core Accessors
    # -----------------------------------------------------

    def get_baseline_tone(self) -> Dict[str, bool]:
        return self.voiceprint.baseline_tone

    def get_sentence_rhythm(self) -> Dict[str, Any]:
        return self.voiceprint.communication_style["sentence_rhythm"]

    def get_pacing_rules(self) -> Dict[str, Any]:
        return self.voiceprint.communication_style["pacing"]

    def get_density_rules(self) -> Dict[str, Any]:
        return self.voiceprint.communication_style["density"]

    def get_signature_phrases(self):
        return self.voiceprint.signature_phrasing

    def get_actor_fusion_weights(self):
        return self.voiceprint.actor_fusion["base_weights"]

    def get_dynamic_shift_range(self):
        return self.voiceprint.actor_fusion["dynamic_shift_range"]

    def get_metaphor_density_rules(self):
        return self.voiceprint.metaphor_density

    def get_forbidden_elements(self):
        return self.voiceprint.forbidden_elements

    # -----------------------------------------------------
    # Emotional Rewrite Parameters
    # -----------------------------------------------------

    def get_global_modulation_weights(self):
        return self.voiceprint.emotional_rewrite_parameters["global_weights"]

    def get_emotion_profile(self, emotion: str) -> Dict[str, float]:
        profiles = self.voiceprint.emotional_rewrite_parameters["emotion_profiles"]
        return profiles.get(emotion, {})

    def get_volatility_smoothing(self):
        return self.voiceprint.emotional_rewrite_parameters["volatility_smoothing"]

    def get_intensity_scaling(self):
        return self.voiceprint.emotional_rewrite_parameters["intensity_scaling"]

    # -----------------------------------------------------
    # Convenience Helpers
    # -----------------------------------------------------

    def get_all(self) -> Dict[str, Any]:
        """Returns the entire voiceprint as a dictionary-like object."""
        return self.voiceprint.__dict__

    def summary(self) -> Dict[str, Any]:
        """Returns a compact summary for debugging."""
        return {
            "version": self.voiceprint.version,
            "tone": self.voiceprint.baseline_tone,
            "pacing": self.voiceprint.communication_style["pacing"],
            "density": self.voiceprint.communication_style["density"],
            "signature_phrasing_count": len(self.voiceprint.signature_phrasing),
            "forbidden_elements": self.voiceprint.forbidden_elements,
        }


# ---------------------------------------------------------
# Singleton Loader Instance
# ---------------------------------------------------------

voiceprint_loader = VoiceprintLoader()