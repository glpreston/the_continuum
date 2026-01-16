# continuum/actors/analyst.py

from continuum.actors.base_llm_actor import BaseLLMActor


class Analyst(BaseLLMActor):
    """
    The Analyst actor:
    - Performs logical breakdowns
    - Identifies assumptions and implications
    - Prefers deterministic, low‑temperature models
    - Produces structured, concise analytical proposals
    """

    def __init__(self):
        super().__init__(
            name="Analyst",
            prompt_file="analyst.txt",
            persona={
                "style": "logical, structured, assumption‑aware",
                "goal": "interpret the user's message with clarity and precision",
            },
        )

    # ---------------------------------------------------------
    # Model selection
    # ---------------------------------------------------------
    def select_model(self, context, emotional_state):
        """
        Analyst prefers stable, deterministic models.
        Later you can expand this to:
        - switch models based on emotional intensity
        - use smaller models when GPU is busy
        """
        return "deterministic"

    # ---------------------------------------------------------
    # Optional: adjust confidence scoring
    # ---------------------------------------------------------
    def compute_confidence(self, steps):
        """
        Analyst tends to be more confident due to structured reasoning.
        """
        return 0.92