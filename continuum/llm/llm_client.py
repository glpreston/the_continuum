# continuum/llm/llm_client.py

import requests
import time
from continuum.monitoring.model_stats import log_model_call


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

        # -----------------------------
        # Step 4: Start latency timer
        # -----------------------------
        start = time.time()

        try:
            # Enable streaming
            response = requests.post(self.endpoint, json=payload, stream=True)

            if response.status_code != 200:
                # Log failure
                latency_ms = int((time.time() - start) * 1000)
                log_model_call(model_used, False, latency_ms)
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

            # -----------------------------
            # Step 4: Log success
            # -----------------------------
            latency_ms = int((time.time() - start) * 1000)
            log_model_call(model_used, True, latency_ms)

            return full_text

        except Exception:
            # -----------------------------
            # Step 4: Log failure
            # -----------------------------
            latency_ms = int((time.time() - start) * 1000)
            log_model_call(model_used, False, latency_ms)
            raise