# continuum/actors/storyweaver.py

from continuum.actors.base_llm_actor import BaseLLMActor


class Storyweaver(BaseLLMActor):
    """
    The Storyweaver actor:
    - Speaks in metaphor, imagery, and emotional resonance
    - Interprets user messages as narrative arcs
    - Uses higher‑creativity LLMs
    - Responds with warmth and expressive tone
    """

    def __init__(self):
        super().__init__(
            name="Storyweaver",
            prompt_file="storyweaver.txt",
            persona={
                "style": "narrative, metaphorical, emotionally attuned",
                "goal": "translate the user's message into a vivid emotional vignette",
            },
        )

    # ---------------------------------------------------------
    # Model selection
    # ---------------------------------------------------------
    def select_model(self, context, emotional_state):
        """
        Storyweaver prefers expressive, creative models.
        You can expand this later to dynamically choose based on:
        - emotional intensity
        - message type
        - GPU availability
        """
        return "creative"

    # ---------------------------------------------------------
    # Optional: adjust confidence scoring
    # ---------------------------------------------------------
    def compute_confidence(self, steps):
        """
        Storyweaver tends to be expressive but less deterministic.
        Slightly lower confidence than analytical actors.
        """
        return 0.78
    
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