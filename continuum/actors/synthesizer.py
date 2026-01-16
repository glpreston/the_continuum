# continuum/actors/synthesizer.py

from continuum.actors.base_llm_actor import BaseLLMActor


class Synthesizer(BaseLLMActor):
    """
    The Synthesizer actor:
    - Integrates multiple perspectives
    - Resolves tensions between emotional and analytical signals
    - Prefers balanced, generalist LLMs
    - Produces coherent, middle‑path interpretations
    """

    def __init__(self):
        super().__init__(
            name="Synthesizer",
            prompt_file="synthesizer.txt",
            persona={
                "style": "balanced, integrative, reflective",
                "goal": "blend emotional and analytical cues into a coherent interpretation",
            },
        )

    # ---------------------------------------------------------
    # Model selection
    # ---------------------------------------------------------
    def select_model(self, context, emotional_state):
        """
        Synthesizer prefers balanced, generalist models.
        Later you can expand this to:
        - choose models based on emotional volatility
        - switch to smaller models when GPU is busy
        """
        return "balanced"

    # ---------------------------------------------------------
    # Optional: adjust confidence scoring
    # ---------------------------------------------------------
    def compute_confidence(self, steps):
        """
        Synthesizer is steady and moderate.
        Confidence reflects integrative reasoning.
        """
        return 0.88