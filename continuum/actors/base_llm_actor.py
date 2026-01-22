# continuum/actors/base_llm_actor.py

import os
from typing import Any

from continuum.actors.base_actor import BaseActor


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
        """
        Fusion‑2.1: return persona template exactly as-is.
        """
        return self.prompt_template

    # ------------------------------------------------------------------
    # Optional postprocess hook
    # ------------------------------------------------------------------
    def _postprocess(self, text: str) -> str:
        return text.strip()

    # ------------------------------------------------------------------
    # Proposal generation (Senate stage)
    # ------------------------------------------------------------------
    def propose(
        self,
        context,
        emotional_state,
        emotional_memory,
        message=None,
        controller=None,
        **kwargs,
    ):
        if controller is None:
            raise ValueError("BaseLLMActor.propose() requires a controller instance.")

        model_info = controller.registry.get(self.model_name)
        if not model_info:
            return {
                "actor": self.name,
                "content": f"[ERROR] No model found: {self.model_name}",
                "confidence": 0.0,
                "reasoning": ["Model registry returned no match"],
                "metadata": {"type": "llm_actor"},
            }

        # Build system-style prompt for Ollama
        persona_prompt = self.build_prompt(
            context=context,
            emotional_state=emotional_state,
            emotional_memory=emotional_memory,
            message=message,
            controller=controller,
            **kwargs,
        )

        # Combine persona + user message
        combined_prompt = (
            persona_prompt
            + "\n\nUser message:\n"
            + str(message).strip()
            + "\n\nAssistant:"
        )

        # Debug: show full prompt sent to Ollama
        if getattr(controller.context, "debug_flags", {}).get("show_prompts"):
            print("\n================= DEBUG: FULL PROMPT =================")
            print(combined_prompt)
            print("=====================================================\n")

        # Generate LLM output
        llm_output = model_info.node.generate(
            prompt=combined_prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        # Debug: raw LLM output BEFORE postprocessing
        if getattr(controller.context, "debug_flags", {}).get("show_prompts"):
            print(f"\n=== DEBUG LLM RAW OUTPUT ({self.name}) ===")
            print(repr(llm_output))
            print("==========================================\n")

        # Postprocess
        clean = self._postprocess(llm_output)

        # Debug: cleaned proposal
        if getattr(controller.context, "debug_flags", {}).get("show_prompts"):
            print(f"\n=== DEBUG RAW PROPOSAL ({self.name}) ===")
            print(clean)
            print("=======================================\n")

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
    # Fusion‑2.1 final response (raw prompt → model → text)
    # ------------------------------------------------------------------
    def respond(self, prompt: str, **kwargs) -> str:

        # Debug: show Fusion prompt
        if getattr(self.controller.context, "debug_flags", {}).get("show_prompts"):
            print("\n================= DEBUG: FUSION PROMPT =================")
            print(prompt)
            print("========================================================\n")

        model_info = self.registry.get(self.model_name)
        if not model_info:
            return f"[ERROR] No model found: {self.model_name}"

        output = model_info.node.generate(
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return self._postprocess(output)