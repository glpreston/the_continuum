# continuum/actors/storyweaver.py
import re
from continuum.actors.base_llm_actor import BaseLLMActor


class Storyweaver(BaseLLMActor):
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
            prompt_file="storyweaver_prompt.txt",
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
        return 0.90

    def propose(self, context, message, controller, emotional_state, emotional_memory):
        llm_proposal = super().propose(
            context=context,
            emotional_state=emotional_state,
            emotional_memory=emotional_memory,
            message=message,
            controller=controller,
        )

        llm_proposal["confidence"] = self.compute_confidence(
            llm_proposal.get("reasoning", [])
        )

        return llm_proposal

    # ---------------------------------------------------------
    # Fusion-friendly response generation (Fusion 2.1)
    # ---------------------------------------------------------
    def respond(self, prompt: str, **kwargs) -> str:
        """
        Produce a short, single-paragraph expressive interpretation.
        Keep it lyrical but compact so Fusion can blend it cleanly.
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