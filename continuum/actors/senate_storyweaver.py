# continuum/actors/senate_storyweaver.py

from continuum.actors.senate_base import SenateBase


class SenateStoryweaver(SenateBase):
    """
    Phase‑4 Senate wrapper for the Storyweaver LLM actor.
    Delegates proposal generation to the underlying LLM actor.
    """

    def __init__(self, llm_actor):
        super().__init__(llm_actor, "SenateStoryweaver")

    def propose(self, context, message, controller, emotional_state, emotional_memory):
        # Delegate to the underlying actor
        llm_proposal = self.llm_actor.propose(
            context=context,
            message=message,
            controller=controller,
            emotional_state=emotional_state,
            emotional_memory=emotional_memory,
        )

        # Tag as Senate output
        llm_proposal["actor"] = "SenateStoryweaver"
        llm_proposal["metadata"]["senate_actor"] = True

        return llm_proposal