# continuum/actors/senate_analyst.py

from continuum.actors.senate_base import SenateBase


class SenateAnalyst(SenateBase):
    """
    Phase‑4 Senate wrapper for the Analyst LLM actor.
    Delegates proposal generation to the underlying LLM actor.
    """

    def __init__(self, llm_actor):
        super().__init__(llm_actor, "SenateAnalyst")

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
        llm_proposal["actor"] = "SenateAnalyst"
        llm_proposal["metadata"]["senate_actor"] = True

        return llm_proposal