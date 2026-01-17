# continuum/orchestrator/continuum_controller.py
# Clean, modular ContinuumController using extracted pipeline components

import uuid
from typing import Dict, Any

from continuum.core.context import ContinuumContext
from continuum.core.turn_logger import TurnLogger

from continuum.emotion.emotion_detector import EmotionDetector
from continuum.emotion.emotional_state_manager import EmotionalStateManager
from continuum.emotion.arc_pipeline import ArcPipeline
from continuum.emotion.state_machine import EmotionalState

from continuum.persona.meta_persona import MetaPersona
from continuum.persona.meta_pipeline import MetaPipeline

from continuum.orchestrator.deliberation_engine import DeliberationEngine
from continuum.orchestrator.fusion_pipeline import FusionPipeline
from continuum.orchestrator.fusion_smoothing import FusionSmoother
from continuum.orchestrator.senate import Senate
from continuum.orchestrator.jury import Jury

from continuum.persona.emotional_memory import EmotionalMemory
from continuum.emotion.emotional_arc_engine import EmotionalArcEngine

from continuum.actors.senate_architect import SenateArchitect
from continuum.actors.senate_storyweaver import SenateStoryweaver
from continuum.actors.senate_analyst import SenateAnalyst
from continuum.actors.senate_synthesizer import SenateSynthesizer

from continuum.orchestrator.model_registry import ModelRegistry

from continuum.actors.storyweaver import Storyweaver
from continuum.actors.analyst import Analyst
from continuum.actors.synthesizer import Synthesizer
from continuum.actors.architect import Architect

from continuum.core.logger import log_info


class ContinuumController:
    """
    Clean, modular orchestrator for The Continuum.
    Coordinates:
      - Emotion detection
      - Emotional state updates
      - Senate + Jury deliberation
      - Fusion 2.0
      - Meta‑Persona rewrite
      - Emotional arcs
      - Turn logging
    """

    def __init__(self):

        # ---------------------------------------------------------
        # Emotional engine (Phase‑4)
        # ---------------------------------------------------------
        self.emotional_memory = EmotionalMemory()
        self.emotional_state = EmotionalState()

        # Model registry (REQUIRED for BaseLLMActor)
        self.registry = ModelRegistry()

        # ---------------------------------------------------------
        # Core state
        # ---------------------------------------------------------
        self.context = ContinuumContext(conversation_id=str(uuid.uuid4()))
        self.context.emotional_state = self.emotional_state
        self.context.emotional_memory = self.emotional_memory

        # Track last final proposal for Meta‑Persona
        self.last_final_proposal = None

        # Actor enable/disable settings
        self.actor_settings = {
            "Architect": {"enabled": True},
            "Storyweaver": {"enabled": True},
            "Analyst": {"enabled": True},
            "Synthesizer": {"enabled": True},
        }

        # Senate actors (Phase‑4 wrappers)
        self.senate = Senate([
            SenateArchitect(),
            SenateStoryweaver(),
            SenateAnalyst(),
            SenateSynthesizer(),
        ])

        # Map Senate wrapper names to underlying LLM actor names
        self.senate_to_llm_map = {
            "SenateArchitect": "Architect",
            "SenateStoryweaver": "Storyweaver",
            "SenateAnalyst": "Analyst",
            "SenateSynthesizer": "Synthesizer",
        }

        # Underlying LLM actors (required by Fusion 2.0)
        self.actors = {
            "Architect": Architect(),
            "Storyweaver": Storyweaver(),
            "Analyst": Analyst(),
            "Synthesizer": Synthesizer(),
        }

        self.turn_logger = TurnLogger()

        # Emotional arc engine
        self.emotional_arc_engine = EmotionalArcEngine()

        # ---------------------------------------------------------
        # Modular pipeline components
        # ---------------------------------------------------------
        self.emotion_detector = EmotionDetector()
        self.state_manager = EmotionalStateManager()
        self.arc_pipeline = ArcPipeline(self.emotional_arc_engine)

        # Fusion
        self.fusion_smoother = FusionSmoother(alpha=0.6)
        self.fusion_pipeline = FusionPipeline(
            smoother=self.fusion_smoother,
            emotional_arc_engine=self.emotional_arc_engine,
        )

        # Meta‑Persona
        self.meta_persona = MetaPersona(
            name="The Continuum",
            voice="Warm, precise, collaborative",
            traits={
                "architect": "Thinks in systems",
                "storyweaver": "Uses metaphor to make complexity intuitive",
                "deliberative": "Surfaces tradeoffs gracefully",
            },
        )
        self.meta_pipeline = MetaPipeline(self.meta_persona)

        # ---------------------------------------------------------
        # Deliberation Engine
        # ---------------------------------------------------------
        self.jury = Jury()
        self.deliberation_engine = DeliberationEngine(
            senate=self.senate,
            jury=self.jury,
        )

        log_info("ContinuumController initialized (modular)", phase="controller")

    # ---------------------------------------------------------
    # Main pipeline
    # ---------------------------------------------------------
    def process_message(self, message: str) -> str:

        # 1. Emotion detection
        raw_state, dominant_emotion, intensity = self.emotion_detector.detect(message)
        self.emotional_memory.add_event(
            raw_state=raw_state,
            dominant_emotion=dominant_emotion,
            metadata={"source": "model"},
        )

        # 2. Emotional state update
        self.emotional_state = self.state_manager.update(
            self.emotional_state,
            raw_state,
        )

        # 3. Senate + Jury
        ranked, final_proposal = self.deliberation_engine.run(
            controller=self,
            context=self.context,
            message=message,
            emotional_state=self.emotional_state,
            emotional_memory=self.emotional_memory,
        )

        # 4. Fusion 2.0
        fusion_weights = self.fusion_pipeline.adjust(final_proposal)
        final_text = self.fusion_pipeline.run(
            fusion_weights=fusion_weights,
            ranked_proposals=ranked,
            controller=self,
        )

        # Store for Meta‑Persona
        self.last_final_proposal = final_proposal

        # 5. Meta‑Persona rewrite
        rewritten = self.meta_pipeline.rewrite(final_text, self)
        self.context.add_assistant_message(rewritten)

        # 6. Emotional arc snapshot
        self.arc_pipeline.record(
            emotional_state=self.emotional_state,
            dominant_emotion=dominant_emotion,
            fusion_weights=fusion_weights,
        )

        # 7. Turn logging
        self.turn_logger.append(
            user_message=message,
            assistant_output=rewritten,
            raw_emotion=raw_state,
            final_proposal=final_proposal,
            dominant_emotion=dominant_emotion,
            intensity=intensity,
        )

        return rewritten