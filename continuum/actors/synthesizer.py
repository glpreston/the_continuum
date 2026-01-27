# continuum/actors/synthesizer.py
from continuum.actors.base_llm_actor import BaseLLMActor
import re

class Synthesizer(BaseLLMActor):
    def __init__(self, name, model_name, fallback_model, personality, system_prompt, temperature, max_tokens, controller):
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
    # Optional: Synthesizer-specific confidence shaping
    # ---------------------------------------------------------
    def compute_confidence(self, steps):
        # Synthesizer tends to be integrative and balanced
        return 0.88

    # ---------------------------------------------------------
    # Phase‑4 propose() — no model argument
    # ---------------------------------------------------------
    def propose(
        self,
        context,
        message,
        controller,
        temperature,
        max_tokens,
        system_prompt,
        memory,
        emotional_state,
        voiceprint,
        metadata,
        telemetry,
    ):
        # Phase‑4: BaseLLMActor handles model + node selection internally
        llm_output = self._run_llm(
            context=context,
            message=message,
            controller=controller,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            memory=memory,
            emotional_state=emotional_state,
            voiceprint=voiceprint,
            metadata=metadata,
            telemetry=telemetry,
        )

        proposal = {
            "actor": self.name,
            "content": llm_output,
            "confidence": self.compute_confidence([]),
            "metadata": metadata,
        }

        return proposal


    # ---------------------------------------------------------
    # Phase‑4 requirement: summarize_reasoning()
    # ---------------------------------------------------------
    def summarize_reasoning(self, proposal):
        """
        Phase‑4: Senate passes the full proposal dict.
        We must extract the content and summarize it.
        """
        if not proposal or "content" not in proposal:
            return "No reasoning available."

        raw = proposal["content"]

        if not isinstance(raw, str):
            return "No reasoning available."

        # Extract first sentence as a lightweight summary
        first_sentence = raw.split(".")[0].strip()

        if len(first_sentence) < 5:
            return "Summary unavailable."

        return first_sentence
    # ---------------------------------------------------------
    # Fusion-friendly response generation (Fusion 2.1)
    # ---------------------------------------------------------
    def respond(self, prompt: str, **kwargs) -> str:
        raw = super().respond(prompt, **kwargs)
        return self._postprocess(raw)

    def _postprocess(self, text: str) -> str:
        # Remove markdown bullets and numbered lists
        text = re.sub(r'[\*\-\•]+', ' ', text)
        text = re.sub(r'\n?\s*\d+\.\s+', ' ', text)

        # Remove boilerplate analysis phrases
        text = re.sub(r"The user's message can be analyzed as follows:?", ' ', text, flags=re.IGNORECASE)
        text = re.sub(r"That's a clear( and also)? concise proposal!? ?", ' ', text, flags=re.IGNORECASE)
        text = re.sub(r"Title:\s*[^\.!\n]+", ' ', text, flags=re.IGNORECASE)

        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text