# continuum/llm/llm_client.py

import requests

class LLMClient:
    """
    Ollama Cloud LLM client.
    Sends prompts to Ollama Cloud using the /api/generate endpoint.
    """

    def __init__(self, endpoint: str = "http://localhost:11434/api/generate"):
        self.endpoint = endpoint

    def generate(self, prompt: str, model: str = None, temperature: float = 0.7, max_tokens: int = 512):
        import json
        import requests

        model_used = model

        payload = {
            "model": model_used,
            "prompt": prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        # Enable streaming
        response = requests.post(self.endpoint, json=payload, stream=True)

        if response.status_code != 200:
            return f"[ERROR] Ollama returned {response.status_code}: {response.text}"

        full_text = ""

        # Ollama streams NDJSON — one JSON object per line
        for line in response.iter_lines():
            if not line:
                continue

            try:
                obj = json.loads(line.decode("utf-8"))
            except Exception:
                continue

            # Accumulate tokens
            if "response" in obj:
                full_text += obj["response"]

            # Stop when Ollama signals completion
            if obj.get("done"):
                break

        return full_text