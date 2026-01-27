#continuum/db/registry/availability_scoring.py
from continuum.db.models.model_nodes import ModelNode
from continuum.db.models.nodes import NodeStatus


class AvailabilityScoringMixin:
    """
    Computes availability score based on:
    - model_nodes.availability
    - node.enabled
    - node.status
    """

    def evaluate_node_availability(self, node, model_name):
        link = (
            self.db.query(ModelNode)
            .filter(ModelNode.node_id == node.id)
            .filter(ModelNode.model_name == model_name)
            .first()
        )

        if not link:
            return 0.0

        if link.availability == "unavailable":
            return 0.0

        if not node.enabled:
            return 0.0

        if node.status == NodeStatus.offline:
            return 0.0

        score = 1.0

        if node.status == NodeStatus.unknown:
            score *= 0.5

        return score