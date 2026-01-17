# continuum/actors/architect.py

from continuum.actors.base_llm_actor import BaseLLMActor


class Architect(BaseLLMActor):
    """
    The Architect actor:
    - Thinks in systems, structures, and dependencies
    - Prefers long‑context, stable models
    - Produces blueprint‑style interpretations
    - Focuses on clarity, modularity, and long‑term coherence
    """

    def __init__(self):
        super().__init__(
            name="Architect",
            prompt_file="architect.txt",
            persona={
                "style": "structured, systems‑oriented, blueprint‑driven",
                "goal": "translate the user's message into a clear structural interpretation",
            },
        )

    # ---------------------------------------------------------
    # Model selection
    # ---------------------------------------------------------
    def select_model(self, context, emotional_state):
        """
        Architect prefers long‑context, stable models.
        Later you can expand this to:
        - choose models based on message complexity
        - switch to smaller models when GPU is busy
        """
        return "long_context"

    # ---------------------------------------------------------
    # Optional: adjust confidence scoring
    # ---------------------------------------------------------
    def compute_confidence(self, steps):
        """
        Architect is methodical and structured.
        Confidence reflects blueprint‑level clarity.
        """
        return 0.94
    
    def propose(self, context, message, controller, emotional_state, emotional_memory):
        """
        Senate-aware proposal method.
        Ensures controller and message are passed through to BaseLLMActor.
        """

        llm_proposal = super().propose(
            context=context,
            emotional_state=emotional_state,
            emotional_memory=emotional_memory,
            message=message,
            controller=controller,
        )

        # Optional: actor-specific confidence logic
        if hasattr(self, "compute_confidence"):
            llm_proposal["confidence"] = self.compute_confidence(
                llm_proposal.get("reasoning", [])
            )

        return llm_proposal