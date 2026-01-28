# continuum/actors/architect.py

from continuum.actors.base_llm_actor import BaseLLMActor

class Architect(BaseLLMActor):
    def __init__(self, controller):
        super().__init__(
            name="Architect",
            prompt_file="architect.txt",
            persona="architect",
            system_prompt="You are the Architect.",
            temperature=0.7,
            max_tokens=512,
            controller=controller,
        )

    # ---------------------------------------------------------
    # Phase‑5 propose() signature
    # ---------------------------------------------------------
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
        Phase‑5 propose(): delegates to BaseLLMActor.generate()
        using the model/node chosen by Router.
        """

        return super().propose(
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