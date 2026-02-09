# continuum/orchestrator/model_registry.py

from continuum.llm.llm_client import LLMClient


# ---------------------------------------------------------
# Ollama Cloud LLM Node (delegates to LLMClient)
# ---------------------------------------------------------
class LLMNode:
    """
    Thin wrapper around LLMClient so BaseLLMActor can call generate().
    """

    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: int = 512):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = LLMClient()

    def generate(
        self,
        prompt: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ):
        return self.client.generate(
            prompt=prompt,
            model=model or self.model_name,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
        )


# ---------------------------------------------------------
# ModelInfo
# ---------------------------------------------------------
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
        self.node = LLMNode(name, temperature=temperature, max_tokens=max_tokens)


# ---------------------------------------------------------
# Model Registry (DB-driven)
# ---------------------------------------------------------
class ModelRegistry:
    """
    Stores ModelInfo objects loaded dynamically from the database.
    """

    def __init__(self):
        self.models = {}  # key: model_name, value: ModelInfo

    def register_model(
        self,
        name: str,
        provider: str,
        context_window: int,
        temperature_default: float,
    ):
        """
        Called by ContinuumController when loading models from DB.
        Stores all model metadata for future use.
        """
        # Use temperature_default as the active temperature for now
        info = ModelInfo(
            name=name,
            temperature=temperature_default,
            max_tokens=context_window,  # temporary placeholder until schema expands
        )

        # Attach DB metadata
        info.provider = provider
        info.context_window = context_window
        info.temperature_default = temperature_default

        self.models[name] = info

    def get(self, model_name: str) -> ModelInfo:
        """
        Retrieve a model by name.
        """
        return self.models.get(model_name)

    def find_best_match(self, actor_name: str) -> ModelInfo:
        """
        Legacy fallback — not used in DB-driven mode,
        but kept for compatibility.
        """
        return next(iter(self.models.values()))