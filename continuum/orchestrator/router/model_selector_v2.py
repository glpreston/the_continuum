#continuum/orchestrator/router/model_selector_v2.py

from sqlalchemy import text
from continuum.core.logger import log_debug, log_error

class ModelSelectorV2:
    """
    Phase‑5 Model Selector (DB‑driven).

    Responsibilities:
      - Pull available models from DB (model_nodes table)
      - Normalize model names (ensure :latest suffix)
      - Return weighted candidates for routing
    """

    def __init__(self, db, logger=None):
        self.db = db
        self.logger = logger or (lambda *args, **kwargs: None)

    def select_models(self, intent_name: str, actor_name: str = None):
        """
        Returns:
            {
                "candidates": [
                    {"model": "llama3.2:latest", "weight": 1.0},
                    {"model": "mistral-openorca:latest", "weight": 1.0},
                    ...
                ]
            }
        """

        # ---------------------------------------------------------
        # 1. Pull all distinct model names from model_nodes
        # ---------------------------------------------------------
        rows = self.db.execute(
            text("SELECT DISTINCT model_name FROM model_nodes")
        ).scalars().all()

        # Fallback if DB is empty
        if not rows:
            rows = ["llama3.2:latest"]

        # ---------------------------------------------------------
        # 2. Normalize names (ensure :latest suffix)
        # ---------------------------------------------------------
        normalized = []
        for m in rows:
            if ":" not in m:
                m = m + ":latest"
            normalized.append(m)

        # ---------------------------------------------------------
        # 3. Build weighted candidate list
        # ---------------------------------------------------------
        candidates = [{"model": m, "weight": 1.0} for m in normalized]

        self.logger("info", f"[ModelSelectorV2] intent={intent_name}, actor={actor_name}")
        self.logger("info", f"[ModelSelectorV2] candidates={candidates}")

        return {"candidates": candidates}