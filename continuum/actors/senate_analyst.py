# continuum/actors/senate_analyst.py

from continuum.actors.senate_base import SenateBase

class SenateAnalyst(SenateBase):
    """
    Modernized Senate wrapper for the Analyst LLM actor.
    Router-aware and simplified.
    """

    def __init__(self, llm_actor):
        super().__init__(llm_actor, "Analyst")

    def propose(
        self,
        context,
        message,
        controller,
        memory,
        emotional_state,
        emotional_memory,
        voiceprint,
        metadata,
        telemetry,
    ):
        llm_proposal = self.llm_actor.propose(
            context=context,
            message=message,
            controller=controller,
            memory=memory,
            emotional_state=emotional_state,
            emotional_memory=emotional_memory,
            voiceprint=voiceprint,
            metadata=metadata,
            telemetry=telemetry,
        )

        llm_proposal["actor"] = "Analyst"
        llm_proposal.setdefault("metadata", {})["senate_actor"] = True
        return llm_proposal