# continuum/db/registry/health_scoring.py
from datetime import datetime
from continuum.db.models.nodes import NodeStatus
from continuum.db.models.node_health import NodeHealth


class HealthScoringMixin:
    """
    Computes node health score based on:
    - node.status
    - last_seen freshness
    - recent node_health records
    """

    def evaluate_node_health(self, node):
        score = 1.0

        # Status
        if node.status == NodeStatus.offline:
            return 0.0
        if node.status == NodeStatus.unknown:
            score *= 0.5

        # Last seen
        if node.last_seen:
            seconds = (datetime.utcnow() - node.last_seen).total_seconds()
            if seconds > 60:
                score *= 0.7
            if seconds > 300:
                score *= 0.3

        # Recent health records
        records = (
            self.db.query(NodeHealth)
            .filter(NodeHealth.node_id == node.id)
            .order_by(NodeHealth.timestamp.desc())
            .limit(5)
            .all()
        )

        for r in records:
            if r.status != "online":
                score *= 0.8

        return max(0.0, min(1.0, score))