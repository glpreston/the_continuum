# continuum/actors/storyweaver.py

from continuum.actors.base_llm_actor import BaseLLMActor

class Storyweaver(BaseLLMActor):
    def __init__(self, controller):
        super().__init__(
            name="Storyweaver",
            prompt_file="storyweaver.txt",
            persona="storyweaver",
            system_prompt="You are the Storyweaver.",
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
        Phase‑5 propose(): delegates to BaseLLMActor.propose()
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