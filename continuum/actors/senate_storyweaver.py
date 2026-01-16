from continuum.actors.base_actor import BaseActor
from continuum.actors.storyweaver import Storyweaver


class SenateStoryweaver(BaseActor):
    """
    Phase‑4 Senate wrapper for the Storyweaver LLM actor.
    Delegates proposal generation to the LLM actor.
    """

    def __init__(self):
        super().__init__("SenateStoryweaver")
        self.llm_actor = Storyweaver()

    def propose(self, context, message, controller, emotional_state, emotional_memory):
        llm_proposal = self.llm_actor.propose(
            context=context,
            emotional_state=emotional_state,
            emotional_memory=emotional_memory,
        )

        llm_proposal["actor"] = "SenateStoryweaver"
        llm_proposal["metadata"]["senate_actor"] = True

        return llm_proposal