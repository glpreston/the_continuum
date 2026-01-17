# continuum/emotion/emotion_detector.py

from typing import Dict, Tuple, Optional
from transformers import pipeline
from continuum.core.logger import log_info, log_debug, log_error


class EmotionDetector:
    """
    Modular emotion detection engine.
    Handles:
      - keyword overrides
      - transformer-based emotion model
      - lazy loading
      - normalized output
    """

    def __init__(self):
        self.model = None

        # Keyword-based overrides
        self.overrides = {
            "overwhelmed": ("sadness", 0.85),
            "burned out": ("sadness", 0.9),
            "burnt out": ("sadness", 0.9),
            "stressed": ("anxiety", 0.8),
            "anxious": ("anxiety", 0.9),
            "worried": ("anxiety", 0.75),
            "frustrated": ("anger", 0.8),
            "angry": ("anger", 0.9),
            "lonely": ("sadness", 0.9),
            "numb": ("sadness", 0.7),
            "tired": ("sadness", 0.6),
            "exhausted": ("sadness", 0.85),
            "confused": ("confusion", 0.8),
        }

    # ---------------------------------------------------------
    # Lazy model loader
    # ---------------------------------------------------------
    def _load_model(self):
        if self.model is None:
            log_info("Loading emotion model pipeline", phase="emotion")
            self.model = pipeline(
                "text-classification",
                model="SamLowe/roberta-base-go_emotions",
                top_k=None,
            )

    # ---------------------------------------------------------
    # Keyword override
    # ---------------------------------------------------------
    def _keyword_override(self, text: str) -> Optional[Tuple[str, float]]:
        text = text.lower()
        for key, (label, intensity) in self.overrides.items():
            if key in text:
                log_debug(
                    f"Keyword emotion override matched: '{key}' → {label} ({intensity})",
                    phase="emotion",
                )
                return label, intensity
        return None

    # ---------------------------------------------------------
    # Main detection entry point
    # ---------------------------------------------------------
    def detect(self, message: str) -> Tuple[Dict[str, float], str, float]:
        """
        Returns:
            raw_state: {emotion: score}
            dominant: str
            intensity: float
        """

        # 1. Keyword override
        override = self._keyword_override(message)
        if override:
            label, score = override
            raw_state = {label: score}
            log_info(
                f"Emotion override applied: {label} ({score:.2f})",
                phase="emotion",
            )
            return raw_state, label, score

        # 2. Model-based detection
        try:
            self._load_model()
            raw = self.model(message)[0]
            raw_state = {entry["label"]: entry["score"] for entry in raw}
            dominant = max(raw_state, key=raw_state.get)
            intensity = raw_state[dominant]

            log_info(
                f"Emotion detected: {dominant} ({intensity:.2f})",
                phase="emotion",
            )

            return raw_state, dominant, intensity

        except Exception as e:
            log_error(f"Emotion detection failed: {e}", phase="emotion")
            return {"neutral": 0.0}, "neutral", 0.0