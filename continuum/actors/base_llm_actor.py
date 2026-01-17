# continuum/actors/base_llm_actor.py

import os
from typing import Any, Dict, Optional

from continuum.actors.base_actor import BaseActor
from continuum.llm.llm_client import LLMClient


class BaseLLMActor(BaseActor):
    """
    Extension of the Phase‑3 BaseActor that adds:
    - Prompt template loading
    - Emotional + memory injection
    - Dynamic model selection
    - LLM proposal generation

    This class does NOT replace BaseActor.
    It simply adds LLM capability for Storyweaver, Analyst, Synthesizer, Architect.
    """

    def __init__(self, name: str, prompt_file: str, persona: Optional[Dict[str, Any]] = None):
        super().__init__(name, persona)
        self.prompt_file = prompt_file
        self.prompt_template = self._load_prompt_template()
        self.llm = LLMClient()

    # ------------------------------------------------------------------
    # Template loading
    # ------------------------------------------------------------------
    def _load_prompt_template(self) -> str:
        """
        Load the actor's prompt template from /actors/prompts/.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(base_dir, "prompts", self.prompt_file)

        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    # ------------------------------------------------------------------
    # Model selection (override per actor)
    # ------------------------------------------------------------------
    def select_model(self, context, emotional_state) -> str:
        """
        Default model selection logic.
        Subclasses override this to choose their preferred LLM.
        """
        return "default"

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------
    def build_prompt(
        self,
        context: Any,
        emotional_state: Any,
        emotional_memory: Any,
        **kwargs,
    ) -> str:
        """
        Fill the actor's prompt template with dynamic values.
        """

        # Emotional state
        dominant = getattr(emotional_state, "label", "neutral")

        # Memory summaries
        memory_text = ""
        if emotional_memory and hasattr(emotional_memory, "summaries"):
            memory_text = "\n".join(emotional_memory.summaries[-5:])

        # Context window
        context_text = (
            context.get_text_window()
            if hasattr(context, "get_text_window")
            else ""
        )

        # Inject values into the template
        prompt = self.prompt_template.format(
            context=context_text,
            dominant_emotion=dominant,
            memory=memory_text,
            **kwargs,
        )

        return prompt

    # ------------------------------------------------------------------
    # LLM‑powered proposal generation
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
        """
        Generate a structured proposal using the actor's LLM.
        Senate-aware: requires controller and message.
        """

        if controller is None:
            raise ValueError("BaseLLMActor.propose() requires a controller instance.")

        # Select model using registry
        model_info = controller.registry.find_best_match(self.name)
        if not model_info:
            return {
                "actor": self.name,
                "content": "[ERROR] No available model for actor: " + self.name,
                "confidence": 0.0,
                "reasoning": ["Model registry returned no match"],
                "metadata": {"type": "llm_actor"},
            }

        # Build prompt
        prompt = self.build_prompt(
            context=context,
            emotional_state=emotional_state,
            emotional_memory=emotional_memory,
            message=message,
            controller=controller,
            **kwargs,
        )

        # Generate output using the selected node + model
        llm_output = model_info.node.generate(
            prompt=prompt,
            model=model_info.name,
        )

        return {
            "actor": self.name,
            "content": llm_output,
            "confidence": 0.85,  # Actors override this
            "reasoning": ["LLM-generated proposal"],
            "metadata": {
                "model": model_info.name,
                "prompt_used": prompt,
                "type": "llm_actor",
                "persona": self.persona,
            },
        }

    # ------------------------------------------------------------------
    # Phase‑4: LLM-powered final response (Fusion 2.0)
    # ------------------------------------------------------------------
    def respond(
        self,
        context: Any,
        selected_proposal: Dict[str, Any],
        emotional_memory: Any,
        emotional_state: Any,
    ) -> str:
        """
        Generate the actor's final response during Fusion 2.0.
        This is DIFFERENT from propose(): it rewrites or expands the
        selected proposal rather than generating a new one.
        """

        # Extract proposal content
        base_text = selected_proposal.get("content", "")

        # Build a prompt that includes the proposal text
        prompt = self.build_prompt(
            context=context,
            emotional_state=emotional_state,
            emotional_memory=emotional_memory,
            proposal_text=base_text,
        )

        # Select model
        model_name = self.select_model(context, emotional_state)

        # Generate final text
        llm_output = self.llm.generate(prompt, model=model_name)

        return llm_output