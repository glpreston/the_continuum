# continuum/actors/synthesizer.py
import re
from continuum.actors.base_llm_actor import BaseLLMActor


class Synthesizer(BaseLLMActor):
    def __init__(
        self,
        name,
        model_name,
        fallback_model,
        personality,
        system_prompt,
        temperature,
        max_tokens,
        controller,
    ):
        super().__init__(
            name=name,
            prompt_file="synthesizer_prompt.txt",
            persona=personality,
            model_name=model_name,
            fallback_model=fallback_model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            controller=controller,
        )

    # ---------------------------------------------------------
    # Model selection
    # ---------------------------------------------------------
    def select_model(self, context, emotional_state):
        return self.model_name  # DB-driven model

    # ---------------------------------------------------------
    # Optional: adjust confidence scoring
    # ---------------------------------------------------------
    def compute_confidence(self, steps):
        return 0.93

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
        # -----------------------------------------------------
        # 1. Read selected model from Senate (if available)
        # -----------------------------------------------------
        selected_model = None
        key = f"selected_model_{self.name}"

        if hasattr(controller.context, "debug_flags"):
            selected_model = controller.context.debug_flags.get(key)

        # Fallback to actor default if selector failed
        model_to_use = selected_model or model or self.model_name

        # -----------------------------------------------------
        # 2. Call BaseLLMActor.propose() with full Phase‑4 args
        # -----------------------------------------------------
        llm_proposal = super().propose(
            context=context,
            message=message,
            controller=controller,
            model_override=model_to_use,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            memory=memory,
            emotional_state=emotional_state,
            voiceprint=voiceprint,
            metadata=metadata,
            telemetry=telemetry,
        )

        # -----------------------------------------------------
        # 3. Confidence scoring
        # -----------------------------------------------------
        llm_proposal["confidence"] = self.compute_confidence(
            llm_proposal.get("reasoning", [])
        )

        return llm_proposal

    # ---------------------------------------------------------
    # Fusion-friendly response generation (Fusion 2.1)
    # ---------------------------------------------------------
    def respond(self, prompt: str, **kwargs) -> str:
        """
        Produce a short, single-paragraph integrative interpretation.
        Keep it balanced and cohesive so Fusion can blend it cleanly.
        """
        raw = super().respond(prompt, **kwargs)
        return self._postprocess(raw)

    def _postprocess(self, text: str) -> str:
        import re

        # Remove markdown bullets and numbered lists
        text = re.sub(r'[\*\-\•]+', ' ', text)          # bullets
        text = re.sub(r'\n?\s*\d+\.\s+', ' ', text)     # numbered lists

        # Strip common analysis boilerplate
        text = re.sub(r"The user's message can be analyzed as follows:?", ' ', text, flags=re.IGNORECASE)
        text = re.sub(r"That's a clear( and also)? concise proposal!? ?", ' ', text, flags=re.IGNORECASE)
        text = re.sub(r"Title:\s*[^\.!\n]+", ' ', text, flags=re.IGNORECASE)

        # Collapse whitespace and keep it to a single paragraph
        text = re.sub(r'\s+', ' ', text).strip()
        return text