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
        context: Any,
        emotional_state: Any,
        emotional_memory: Any,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a structured proposal using the actor's LLM.
        This overrides BaseActor.propose() but keeps the same return format.
        """

        model_name = self.select_model(context, emotional_state)
        prompt = self.build_prompt(context, emotional_state, emotional_memory, **kwargs)

        llm_output = self.llm.generate(prompt, model=model_name)

        return {
            "actor": self.name,
            "content": llm_output,
            "confidence": 0.85,  # LLM actors can override this later
            "reasoning": ["LLM‑generated proposal"],  # placeholder for Senate/Jury
            "metadata": {
                "model": model_name,
                "prompt_used": prompt,
                "type": "llm_actor",
                "persona": self.persona,
            },
        }