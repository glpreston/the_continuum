# continuum/actors/senate_analyst.py

from continuum.actors.senate_base import SenateBase


class SenateAnalyst(SenateBase):
    """
    Phase‑4 Senate wrapper for the Analyst LLM actor.
    Delegates proposal generation to the underlying LLM actor.
    """

    def __init__(self, llm_actor):
        super().__init__(llm_actor, "SenateAnalyst")

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
        # Delegate to the underlying LLM actor using the Phase‑4 signature
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
        llm_proposal["actor"] = "SenateAnalyst"
        llm_proposal["metadata"]["senate_actor"] = True

        return llm_proposal