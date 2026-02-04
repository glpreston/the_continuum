# continuum/llm/llm_client.py
# Modernized, Router-aware LLM client

import requests
import json


class LLMClient:
    """
    Phase‑5 LLM Client.

    Stateless, Router-aware, and multi-node capable.

    The caller provides:
      - endpoint (from NodeSelectorV2)
      - model (from ModelSelectorV2)
      - prompt
      - temperature
      - max_tokens

    This client simply executes the request.
    """
      
    def __init__(self, default_endpoint="http://localhost:11434/api/generate"):
        self.default_endpoint = default_endpoint
        self.endpoint = default_endpoint
        self.warm_cache = {}   # ⭐ (endpoint, model) → warmed?

    # ---------------------------------------------------------
    # Main LLM call
    # ---------------------------------------------------------
    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        endpoint: str = None,
    ):
        endpoint = endpoint or self.default_endpoint

        # ⭐ Warm the model on this node
        self.warm_model(model, endpoint)

        payload = {
            "model": model,
            "prompt": prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            response = requests.post(endpoint, json=payload, stream=True)
        except Exception as e:
            return f"[ERROR] LLM request failed: {e}"

        if response.status_code != 200:
            return f"[ERROR] LLM returned {response.status_code}: {response.text}"

        full_text = ""

        for line in response.iter_lines():
            if not line:
                continue
            try:
                obj = json.loads(line.decode("utf-8"))
            except Exception:
                continue

            if "response" in obj:
                full_text += obj["response"]

            if obj.get("done"):
                break

        return full_text

    
    def warm_model(self, model, endpoint):
        key = (endpoint, model)

        # Already warm?
        if key in self.warm_cache:
            return

        # Warm-up request (very cheap)
        payload = {
            "model": model,
            "prompt": "warmup",
            "options": {"num_predict": 1}
        }

        try:
            requests.post(endpoint, json=payload, timeout=2)
        except Exception:
            pass  # Warm-up failures shouldn't block anything

        self.warm_cache[key] = True    