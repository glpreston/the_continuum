# orchestrator/router/node_selector_v2.py

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker
import random


LoggerCallable = Callable[[str], None]


@dataclass
class NodeRecord:
    id: int
    name: str
    host: str
    health_score: float
    quarantined: bool
    available_memory_gb: float


class NodeSelectorV2:
    """
    Phase‑5 Node Selector (health‑aware, memory‑aware, reality‑aware).

    Responsibilities:
      - Fetch nodes hosting a given model (from model_nodes)
      - Join with models + nodes + node_health
      - Filter out nodes that cannot load the model (memory)
      - Filter out quarantined nodes
      - Weighted lottery based on health_score
      - Provide alternates sorted by health_score
    """

    def __init__(self, db: Any, logger: Optional[LoggerCallable] = None):
        self.db = db
        self.logger = logger

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    def _get_session(self) -> Session:
        if isinstance(self.db, Session):
            return self.db
        if isinstance(self.db, sessionmaker):
            return self.db()
        if callable(self.db):
            return self.db()
        raise TypeError("db must be a Session, sessionmaker, or callable returning a Session")

    def _log(self, msg: str):
        if self.logger:
            try:
                self.logger("info", msg)
            except Exception:
                pass
        else:
            print(msg)

    # ---------------------------------------------------------
    # Fetch nodes + health + memory
    # ---------------------------------------------------------
    def fetch_model_nodes(self, model_name: str) -> List[NodeRecord]:
        """
        Uses your actual schema:
        model_nodes(model_id, node_id)
        models(id, name, required_memory_gb)
        nodes(id, name, host, available_memory_gb)
        node_health(node_id, health_score, quarantined)
        """

        session = self._get_session()

        rows = (
            session.execute(
                text(
                    """
                    SELECT
                        n.id,
                        n.name,
                        n.host,
                        n.available_memory_gb,
                        nh.health_score,
                        nh.quarantined,
                        m.required_memory_gb

                    FROM model_nodes mn
                    JOIN models m ON m.id = mn.model_id
                    JOIN nodes n ON n.id = mn.node_id
                    LEFT JOIN node_health nh ON nh.node_id = n.id

                    WHERE m.name = :model_name
                    """
                ),
                {"model_name": model_name},
            )
            .mappings()
            .all()
        )

        nodes = []
        for row in rows:
            nodes.append(
                NodeRecord(
                    id=row["id"],
                    name=row["name"],
                    host=row["host"],
                    health_score=row["health_score"] if row["health_score"] is not None else 1.0,
                    quarantined=bool(row["quarantined"]) if row["quarantined"] is not None else False,
                    available_memory_gb=row["available_memory_gb"] or 0.0,
                )
            )

        self._log(f"[NodeSelectorV2] Found {len(nodes)} nodes for model '{model_name}'")
        return nodes

    # ---------------------------------------------------------
    # Weighted lottery
    # ---------------------------------------------------------
    def _weighted_lottery(self, nodes: List[NodeRecord]) -> NodeRecord:
        total = sum(n.health_score for n in nodes)
        if total <= 0:
            return max(nodes, key=lambda n: n.health_score)

        r = random.uniform(0, total)
        cumulative = 0.0

        for node in nodes:
            cumulative += node.health_score
            if r <= cumulative:
                return node

        return nodes[-1]

    # ---------------------------------------------------------
    # Main selection logic
    # ---------------------------------------------------------
    def select_node(self, model_name: str, required_memory_gb: float) -> Dict[str, Any]:
        nodes = self.fetch_model_nodes(model_name)

        if not nodes:
            self._log(f"[NodeSelectorV2] No nodes found for model '{model_name}'")
            return {"selected_node": None, "candidate_nodes": []}

        # 1. Filter out nodes that cannot load the model
        nodes = [
            n for n in nodes
            if n.available_memory_gb >= required_memory_gb
        ]

        if not nodes:
            self._log(
                f"[NodeSelectorV2] No nodes have enough memory for model '{model_name}' "
                f"(required={required_memory_gb} GB)"
            )
            return {"selected_node": None, "candidate_nodes": []}

        # 2. Filter out quarantined nodes
        healthy_nodes = [n for n in nodes if not n.quarantined]

        if not healthy_nodes:
            fallback = max(nodes, key=lambda n: n.health_score)
            self._log(
                f"[NodeSelectorV2] All nodes quarantined for model '{model_name}', "
                f"fallback={fallback.id}"
            )
            return {
                "selected_node": fallback.__dict__,
                "candidate_nodes": [n.__dict__ for n in nodes],
            }

        # 3. Weighted lottery
        selected = self._weighted_lottery(healthy_nodes)

        # 4. Alternates
        alternates = sorted(
            [n for n in healthy_nodes if n.id != selected.id],
            key=lambda n: n.health_score,
            reverse=True,
        )

        self._log(
            f"[NodeSelectorV2] Selected node {selected.id} "
            f"('{selected.name}' @ {selected.host}) "
            f"score={selected.health_score:.3f}"
        )

        return {
            "selected_node": selected.__dict__,
            "candidate_nodes": [n.__dict__ for n in healthy_nodes],
            "available_nodes": [n.__dict__ for n in healthy_nodes],   # ⭐ NEW
            "alternates": [n.__dict__ for n in alternates],
        }    