# continuum/orchestrator/router/node_discovery.py

import requests
from continuum.core.logger import log_error, log_info


# Nodes you want to probe
NODES = [
    ("myplex", "http://myplex:11434"),
    ("Netty", "http://netty:11434"),
    ("Gamer", "http://gamer:11434"),
]


class LiveModelRecord:
    """
    Thin compatibility wrapper so existing UI code can keep using:

        lm.name
        lm.node
        lm.avg_health
        lm.quarantined
        lm.required_memory_gb
        lm.max_node_memory_gb
        lm.is_vision

    even though discovery is now dict-based.
    """

    def __init__(self, node: str, host: str, model_name: str, details: dict | None = None):
        details = details or {}

        self.name = model_name
        self.node = node
        self.host = host

        # Optional / best-effort fields from details
        self.avg_health = details.get("avg_health", None)
        self.quarantined = details.get("quarantined", False)
        self.required_memory_gb = details.get("required_memory_gb", None)
        self.max_node_memory_gb = details.get("max_node_memory_gb", None)
        self.is_vision = details.get("is_vision", False)

    def __repr__(self) -> str:
        return f"<LiveModelRecord name={self.name!r} node={self.node!r}>"


def discover_live_models():
    """
    Phase‑5 discovery:

    - Queries each node's /api/tags endpoint
    - Wraps results in LiveModelRecord for backward compatibility
    - Safe for existing UI pages that expect lm.name, lm.node, etc.
    """

    live_models: list[LiveModelRecord] = []

    for node_name, base_url in NODES:
        tags_url = f"{base_url}/api/tags"
        log_info(f"[Discovery] Querying {node_name} at {tags_url}")

        try:
            response = requests.get(tags_url, timeout=2)
            response.raise_for_status()
            data = response.json()

            # Expected structure: {"models": [{"name": "...", "details": {...}}, ...]}
            models = data.get("models", [])

            for m in models:
                model_name = m.get("name")
                details = m.get("details", {}) or {}

                if not model_name:
                    continue

                live_models.append(
                    LiveModelRecord(
                        node=node_name,
                        host=base_url,
                        model_name=model_name,
                        details=details,
                    )
                )

            log_info(f"[Discovery] {node_name}: found {len(models)} models")

        except Exception as e:
            log_error(
                f"[Discovery] ERROR contacting node {node_name} ({tags_url}): {e}"
            )

    log_info(f"[Discovery] Total live models discovered: {len(live_models)}")
    return live_models