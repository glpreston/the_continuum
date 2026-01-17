# continuum/orchestrator/model_registry.py

class LLMNode:
    """
    Minimal LLM node wrapper.
    Must expose a .generate(prompt, model, temperature, max_tokens) method.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str, model: str = None, temperature: float = 0.5, max_tokens: int = 512):
        """
        Placeholder implementation.
        Replace this with your actual LLM backend call.
        """
        model_used = model or self.model_name
        return f"[{model_used} OUTPUT] {prompt}"


class ModelInfo:
    """
    Holds model configuration for an actor.
    BaseLLMActor expects:
      - .node
      - .name
      - .temperature
      - .max_tokens
    """

    def __init__(self, name: str, temperature: float = 0.5, max_tokens: int = 512):
        self.name = name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.node = LLMNode(name)


class ModelRegistry:
    """
    Maps actor names to ModelInfo objects.
    """

    def __init__(self):
        self.models = {
            "Architect": ModelInfo("gpt-4", temperature=0.2),
            "Storyweaver": ModelInfo("gpt-4", temperature=0.8),
            "Analyst": ModelInfo("gpt-4", temperature=0.1),
            "Synthesizer": ModelInfo("gpt-4", temperature=0.4),
        }

    def find_best_match(self, actor_name: str) -> ModelInfo:
        return self.models.get(actor_name, self.models["Architect"])