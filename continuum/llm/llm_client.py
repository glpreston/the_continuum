# continuum/llm/llm_client.py

class LLMClient:
    """
    Minimal stub LLM client.
    Allows the system to run end-to-end before real models are integrated.
    """

    def __init__(self):
        pass

    def generate(self, prompt: str, model: str = "default") -> str:
        """
        Returns a placeholder response so the pipeline can be tested.
        """
        # Keep it short so debug panels remain readable
        preview = prompt[:200].replace("\n", " ")

        return (
            f"[LLM STUB OUTPUT | model={model}] "
            f"(preview of prompt: {preview}...)"
        )