# continuum/persona/meta_pipeline.py

from continuum.core.logger import log_info
from continuum.persona.meta_persona import MetaPersona
from continuum.emotion.state_machine import EmotionalState
from continuum.persona.emotional_memory import EmotionalMemory
from continuum.core.context import ContinuumContext


class MetaPipeline:
    """
    Handles the Meta‑Persona rewrite stage.
    Responsibilities:
      - apply emotional continuity
      - apply Meta‑Persona voice and traits
      - rewrite the fused text
    """

    def __init__(self, meta_persona: MetaPersona):
        self.meta_persona = meta_persona

    # ---------------------------------------------------------
    # APPLY META‑PERSONA REWRITE
    # ---------------------------------------------------------
    def rewrite(
        self,
        text: str,
        controller,
    ) -> str:
        """
        Applies Meta‑Persona rewrite to the fused text.
        """

        log_info("Applying Meta-Persona rewrite", phase="meta_persona")

        # Update emotional continuity
        self.meta_persona.set_emotional_continuity(
            volatility=controller.emotional_state.volatility,
            confidence=controller.emotional_state.confidence,
            arc_label=controller.emotional_arc_engine.classify_arc(),
        )

        # Apply rewrite
        rewritten = self.meta_persona.render(
            text,
            controller,
            controller.context,
            controller.emotional_state,
            controller.emotional_memory,
        )

        return rewritten