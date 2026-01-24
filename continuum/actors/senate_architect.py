# continuum/actors/senate_architect.py

from continuum.actors.senate_base import SenateBase


class SenateArchitect(SenateBase):
    """
    Phase‑4 Senate wrapper for the Architect LLM actor.
    Delegates proposal generation to the underlying LLM actor.
    """

    def __init__(self, llm_actor):
        super().__init__(llm_actor, "Architect")

    def propose(
        self,
        context,
        message,
        controller,
        model,
        temperature,
        max_tokens,
        system_prompt,
        memory,
        emotional_state,
        voiceprint,
        metadata,
        telemetry,
    ):
        # Delegate to the underlying LLM actor
        llm_proposal = self.llm_actor.propose(
            context=context,
            message=message,
            controller=controller,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            memory=memory,
            emotional_state=emotional_state,
            voiceprint=voiceprint,
            metadata=metadata,
            telemetry=telemetry,
        )

        # Tag as Senate output
        llm_proposal["actor"] = "Architect"
        llm_proposal.setdefault("metadata", {})["senate_actor"] = True

        return llm_proposal