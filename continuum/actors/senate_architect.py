from continuum.actors.base_actor import BaseActor
from continuum.actors.architect import Architect


class SenateArchitect(BaseActor):
    """
    Phase‑4 Senate wrapper for the Architect LLM actor.
    Delegates proposal generation to the LLM actor.
    """

    def __init__(self):
        super().__init__("SenateArchitect")
        self.llm_actor = Architect()

    def propose(self, context, message, controller, emotional_state, emotional_memory):
        llm_proposal = self.llm_actor.propose(
            context=context,
            emotional_state=emotional_state,
            emotional_memory=emotional_memory,
        )

        llm_proposal["actor"] = "SenateArchitect"
        llm_proposal["metadata"]["senate_actor"] = True

        return llm_proposal