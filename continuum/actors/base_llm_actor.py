# continuum/actors/base_llm_actor.py

import os

class BaseLLMActor:
    def __init__(
        self,
        name,
        prompt_file,
        persona,
        model_name,
        fallback_model,
        system_prompt,
        temperature,
        max_tokens,
        controller,
    ):
        self.name = name
        self.prompt_file = prompt_file
        self.persona = persona
        self.model_name = model_name
        self.fallback_model = fallback_model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.controller = controller

    # ---------------------------------------------------------
    # Load persona prompt from /actors/prompts/
    # ---------------------------------------------------------
    def load_persona_prompt(self):
        base = os.path.join(os.path.dirname(__file__), "prompts")
        path = os.path.join(base, self.prompt_file)

        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"[ERROR: could not load persona prompt {self.prompt_file}: {e}]"

    # ---------------------------------------------------------
    # Phase‑4 LLM execution (model + node selection inside)
    # ---------------------------------------------------------
    def _run_llm(
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
        # 1. Model selection
        model_name = controller.model_selector.select_model(
            actor_name=self.name,
            requested_model=self.model_name,
            role="proposal",
        )

        # 2. Load persona prompt
        persona_prompt = self.load_persona_prompt()

        # 3. Build final prompt
        prompt = (
            f"{self.system_prompt}\n\n"
            f"{persona_prompt}\n\n"
            f"User: {message}"
        )

        # 4. Node selection
        node = controller.node_selector.select_node(model_name)

        # 5. Override endpoint
        endpoint = f"{node.base_url}/api/generate"
        original_endpoint = controller.llm_client.endpoint
        controller.llm_client.endpoint = endpoint

        try:
            response = controller.llm_client.generate(
                prompt=prompt,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        finally:
            controller.llm_client.endpoint = original_endpoint

        return response

    # ---------------------------------------------------------
    # Phase‑4 respond() (used by Fusion)
    # ---------------------------------------------------------
    def respond(self, prompt: str, **kwargs) -> str:
        return prompt