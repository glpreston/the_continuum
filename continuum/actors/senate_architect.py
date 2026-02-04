from continuum.actors.senate_base import SenateBase

class SenateArchitect(SenateBase):
    """
    Modernized Senate wrapper for the Architect LLM actor.
    Router-aware, model-agnostic, and simplified.
    """

    def __init__(self, llm_actor):
        super().__init__("Architect", llm_actor)

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
        routing=None,
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
            routing=routing,
        )

        llm_proposal["actor"] = "Architect"
        llm_proposal.setdefault("metadata", {})["senate_actor"] = True

        return llm_proposal