# continuum/actors/senate_analyst.py
from continuum.actors.base_actor import BaseActor
from continuum.actors.analyst import Analyst


class SenateAnalyst(BaseActor):
    """
    Phase‑4 Senate wrapper for the Analyst LLM actor.
    Delegates proposal generation to the LLM actor.
    """

    def __init__(self):
        super().__init__("SenateAnalyst")
        self.llm_actor = Analyst()

    def propose(
        self,
        context,
        message,
        controller,
        emotional_state,
        emotional_memory,
    ):
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