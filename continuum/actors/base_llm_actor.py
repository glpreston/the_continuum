import os
from typing import Any

from continuum.actors.base_actor import BaseActor
from continuum.core.logger import log_error


class BaseLLMActor(BaseActor):
    """
    DB‑driven LLM actor base class.
    Fusion‑2.1 version:
    - Persona prompt is treated as a system instruction
    - User message is appended after the persona prompt
    - No context/emotion/memory injection
    """

    def __init__(
        self,
        name: str,
        prompt_file: str,
        persona: dict,
        model_name: str,
        fallback_model: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int,
        controller,
    ):
        super().__init__(name, persona)

        # Load persona prompt
        self.prompt_file = prompt_file
        self.prompt_template = self._load_prompt_template()

        # DB-driven fields
        self.model_name = model_name
        self.fallback_model = fallback_model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Controller + registry
        self.controller = controller
        self.registry = controller.registry

    # ------------------------------------------------------------------
    # Template loading
    # ------------------------------------------------------------------
    def _load_prompt_template(self) -> str:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(base_dir, "prompts", self.prompt_file)

        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    # ------------------------------------------------------------------
    # Fusion‑2.1: persona prompt only
    # ------------------------------------------------------------------
    def build_prompt(
        self,
        context: Any,
        emotional_state: Any,
        emotional_memory: Any,
        **kwargs,
    ) -> str:
        return self.prompt_template

    # ------------------------------------------------------------------
    # NEW: Safe postprocess override
    # ------------------------------------------------------------------
    def _postprocess(self, output):
        """
        Ensures the LLM output is always treated as a clean string.
        Handles:
        - Dummy model output (string)
        - Real LLM output (string)
        - Unexpected dict formats
        """
        log_error(
            f"[FORENSICS] _postprocess received type={type(output)} value={repr(output)}",
            phase="senate",
        )

        # If the model returns a dict, extract the content
        if isinstance(output, dict):
            output = output.get("content", "")

        # Ensure output is a string
        if not isinstance(output, str):
            output = str(output)

        return output.strip()

    # ------------------------------------------------------------------
    # Proposal generation
    # ------------------------------------------------------------------
    def propose(
        self,
        context,
        message,
        controller,
        model_override,
        temperature,
        max_tokens,
        system_prompt,
        memory,
        emotional_state,
        voiceprint,
        metadata,
        telemetry,
        **kwargs,
    ):
        if controller is None:
            raise ValueError("BaseLLMActor.propose() requires a controller instance.")

        # ---------------------------------------------------------
        # MODEL SELECTION (Senate-driven)
        # ---------------------------------------------------------
        model_to_use = model_override or self.model_name
        model_info = controller.registry.get(model_to_use)

        if model_info is None:
            # Fallback: use the first available model from the registry
            if controller.registry.models:
                fallback_info = next(iter(controller.registry.models.values()))
                log_error(
                    f"[MODEL FALLBACK] No model_info for '{model_to_use}', "
                    f"falling back to '{fallback_info.name}'",
                    phase="senate",
                )
                model_info = fallback_info
            else:
                raise RuntimeError(
                    f"No models available in registry; tried '{model_to_use}'."
                )

        print("MODEL INFO:", model_info)

        # DEBUG: sanity check
        log_error(
            f"[DEBUG] In {self.name}.propose(): controller={type(controller)}, "
            f"controller.registry={repr(getattr(controller, 'registry', None))} "
            f"type={type(getattr(controller, 'registry', None))}",
            phase="senate",
        )

        # ---------------------------------------------------------
        # Build system-style prompt for Ollama
        # ---------------------------------------------------------
        persona_prompt = self.build_prompt(
            context=context,
            emotional_state=emotional_state,
            emotional_memory=memory,
            message=message,
            controller=controller,
            **kwargs,
        )

        combined_prompt = (
            persona_prompt
            + "\n\nUser message:\n"
            + str(message).strip()
            + "\n\nAssistant:"
        )

        # ---------------------------------------------------------
        # Generate LLM output
        # ---------------------------------------------------------
        llm_output = model_info.node.generate(
            prompt=combined_prompt,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )

        log_error(
            f"[FORENSICS] llm_output type={type(llm_output)} value={repr(llm_output)}",
            phase="senate",
        )

        clean = self._postprocess(llm_output)

        return {
            "actor": self.name,
            "content": clean,
            "confidence": 0.85,
            "reasoning": ["LLM-generated proposal"],
            "metadata": {
                "model": model_info.name,
                "prompt_used": persona_prompt,
                "type": "llm_actor",
                "persona": self.persona,
            },
        }

    # ------------------------------------------------------------------
    # Fusion‑2.1 final response
    # ------------------------------------------------------------------
    def respond(self, prompt: str, **kwargs) -> str:

        # MODEL SELECTION (Senate-driven)
        model_to_use = kwargs.get("model_override") or self.model_name

        model_info = self.registry.get(model_to_use)
        if not model_info:
            return f"[ERROR] No model found: {model_to_use}"

        output = model_info.node.generate(
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return self._postprocess(output)