#continuum/orchestrator/nodeselector_v2.py

import random
from sqlalchemy import text


class NodeSelectorV2:

    def __init__(self, db, logger=None):
        self.db = db
        self.logger = logger or (lambda *args, **kwargs: None)

    # -----------------------------------
    # Fetch nodes hosting the model
    # -----------------------------------

    def fetch_model_nodes(self, model_name):
        rows = self.db.execute(
            text("""
                SELECT
                    n.id,
                    n.name,
                    n.type,
                    n.host,
                    n.provider,
                    n.api_key_env,
                    n.enabled,
                    n.status,
                    nh.latency_ms,
                    nh.status AS health_status
                FROM model_nodes mn
                JOIN nodes n ON mn.node_id = n.id
                LEFT JOIN node_health nh ON nh.node_id = n.id
                WHERE mn.model_name = :model_name
            """),
            {"model_name": model_name}
        ).mappings().all()

        # Convert SQLAlchemy RowMapping → dict
        return [dict(r) for r in rows]

    # -----------------------------------
    # Compute health score
    # -----------------------------------
    def compute_health(self, node):
        if not node["enabled"]:
            return 0.0

        status_score = 1.0 if node["status"] == "healthy" else 0.3
        latency_score = 1.0 / (1.0 + (node["latency_ms"] or 200))
        health_status_score = 1.0 if node["health_status"] == "ok" else 0.5

        return (0.5 * status_score) + (0.3 * latency_score) + (0.2 * health_status_score)

    # -----------------------------------
    # Weighted lottery
    # -----------------------------------
    def weighted_choice(self, nodes):
        weights = [n["health_score"] for n in nodes]
        total = sum(weights)
        if total == 0:
            return None
        normalized = [w / total for w in weights]
        return random.choices(nodes, weights=normalized, k=1)[0]

    # -----------------------------------
    # Main selection function
    # -----------------------------------
    def select_node(self, model_name):
        nodes = self.fetch_model_nodes(model_name)

        if not nodes:
            raise RuntimeError(f"No nodes host model '{model_name}'")

        # Compute health scores
        for n in nodes:
            n.setdefault("enabled", True)
            n.setdefault("latency_ms", 200)
            n.setdefault("health_status", "ok")
            n["health_score"] = self.compute_health(n)

        # Filter healthy nodes
        healthy = [n for n in nodes if n["health_score"] > 0.3]

        # Weighted lottery
        selected = self.weighted_choice(healthy) if healthy else None

        # Fallback: choose least-bad node
        if not selected:
            nodes_sorted = sorted(nodes, key=lambda x: x["health_score"], reverse=True)
            selected = nodes_sorted[0]

        # Build alternates list
        alternates = sorted(
            [n for n in nodes if n["id"] != selected["id"]],
            key=lambda x: x["health_score"],
            reverse=True
        )

        result = {
            "model": model_name,
            "selected_node": selected,
            "alternates": alternates
        }

        self.logger("info", f"NodeSelector v2 result: {result}")
        return result