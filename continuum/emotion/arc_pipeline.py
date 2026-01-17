# continuum/emotion/arc_pipeline.py

from typing import Dict
from continuum.core.logger import log_info
from continuum.emotion.state_machine import EmotionalState
from continuum.emotion.emotional_arc_engine import EmotionalArcEngine


class ArcPipeline:
    """
    Handles emotional arc snapshots.
    Responsibilities:
      - record emotional state transitions
      - store dominant emotion
      - store fusion weights
    """

    def __init__(self, arc_engine: EmotionalArcEngine):
        self.arc_engine = arc_engine

    # ---------------------------------------------------------
    # RECORD SNAPSHOT
    # ---------------------------------------------------------
    def record(
        self,
        emotional_state: EmotionalState,
        dominant_emotion: str,
        fusion_weights: Dict[str, float],
    ):
        """
        Records a snapshot of the emotional arc.
        """

        log_info("Recording emotional arc snapshot", phase="emotion_arc")

        self.arc_engine.record_snapshot(
            emotional_state=emotional_state,
            dominant_emotion=dominant_emotion,
            fusion_weights=fusion_weights or {},
        )