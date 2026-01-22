# continuum/orchestrator/controller_pipelines.py
# Pipeline initialization for ContinuumController

from continuum.emotion.emotion_detector import EmotionDetector
from continuum.emotion.emotional_state_manager import EmotionalStateManager
from continuum.emotion.arc_pipeline import ArcPipeline
from continuum.emotion.emotional_arc_engine import EmotionalArcEngine

from continuum.orchestrator.fusion_pipeline import FusionPipeline
from continuum.orchestrator.fusion_smoothing import FusionSmoother

from continuum.persona.meta_persona import MetaPersona
from continuum.persona.meta_pipeline import MetaPipeline

from continuum.core.logger import log_debug


def initialize_pipelines(controller):
    """
    Initializes all pipeline components:
      - Emotion detection
      - Emotional state manager
      - Emotional arc engine + pipeline
      - Fusion pipeline
      - Meta‑Persona + Meta‑Pipeline
    """

    # ---------------------------------------------------------
    # 1. Emotion detection + state manager
    # ---------------------------------------------------------
    controller.emotion_detector = EmotionDetector()
    controller.state_manager = EmotionalStateManager()

    # ---------------------------------------------------------
    # 2. Emotional arc engine + pipeline
    # ---------------------------------------------------------
    controller.emotional_arc_engine = EmotionalArcEngine()
    controller.arc_pipeline = ArcPipeline(controller.emotional_arc_engine)

    # ---------------------------------------------------------
    # 3. Fusion pipeline
    # ---------------------------------------------------------
    controller.fusion_smoother = FusionSmoother(alpha=0.6)
    controller.fusion_pipeline = FusionPipeline(
        smoother=controller.fusion_smoother,
        emotional_arc_engine=controller.emotional_arc_engine,
    )

    # ---------------------------------------------------------
    # 4. Meta‑Persona + Meta‑Pipeline
    # ---------------------------------------------------------
    controller.meta_persona = MetaPersona(
        name="The Continuum",
        voice="Warm, precise, collaborative",
        traits={
            "architect": "Thinks in systems",
            "storyweaver": "Uses metaphor to make complexity intuitive",
            "deliberative": "Surfaces tradeoffs gracefully",
        },
    )

    controller.meta_pipeline = MetaPipeline(controller.meta_persona)

    log_debug("[PIPELINES] Emotion, Fusion, and Meta‑Persona pipelines initialized", phase="controller")