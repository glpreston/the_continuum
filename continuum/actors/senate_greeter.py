from continuum.actors.senate_base import SenateBase

class SenateGreeter(SenateBase):
    """
    Senate wrapper for the Greeter actor.
    """

    def __init__(self, llm_actor):
        # Correct order: name first, actor second
        super().__init__("Greeter", llm_actor)

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

        # Tag correctly
        llm_proposal["actor"] = "Greeter"
        llm_proposal.setdefault("metadata", {})["senate_actor"] = True

        return llm_proposal