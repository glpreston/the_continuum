# continuum/actors/senate_architect.py

from continuum.actors.senate_base import SenateBase

class SenateArchitect(SenateBase):
    """
    Modernized Senate wrapper for the Architect LLM actor.
    Router-aware, model-agnostic, and simplified.

    Delegates proposal generation to the underlying LLM actor,
    which now uses controller.last_routing_decision for model/node selection.
    """

    def __init__(self, llm_actor):
        super().__init__(llm_actor, "Architect")

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
        """
        Modernized propose() signature:
        - No model
        - No temperature
        - No max_tokens
        - No system_prompt

        All of those are now handled by:
        - Router (model + node)
        - BaseLLMActor (temperature, max_tokens, system_prompt)
        """

        # Delegate to the underlying LLM actor
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

        # Tag as Senate output
        llm_proposal["actor"] = "Architect"
        llm_proposal.setdefault("metadata", {})["senate_actor"] = True

        return llm_proposal