# continuum/db/registry/routing.py
from .health_scoring import HealthScoringMixin
from .performance_scoring import PerformanceScoringMixin
from .availability_scoring import AvailabilityScoringMixin


class RoutingMixin(
    HealthScoringMixin,
    PerformanceScoringMixin,
    AvailabilityScoringMixin
):
    """
    Combines all scoring systems and selects best node.
    """

    def score_node_for_model(self, node, model_name):
        health = self.evaluate_node_health(node)
        perf = self.evaluate_node_performance(node, model_name)
        avail = self.evaluate_node_availability(node, model_name)

        if avail == 0.0:
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                0.5 * health +
                0.3 * perf +
                0.2 * avail
            )
        )

    def get_best_node_for_model(self, model_name):
        node_ids = self.get_nodes_for_model(model_name)
        scored = []

        for nid in node_ids:
            node = self.get_node(nid)
            if not node:
                continue
            score = self.score_node_for_model(node, model_name)
            scored.append((score, node))

        scored.sort(reverse=True, key=lambda x: x[0])
        return scored[0][1] if scored else None

    def get_ranked_nodes_for_model(self, model_name):
        node_ids = self.get_nodes_for_model(model_name)
        scored = []

        for nid in node_ids:
            node = self.get_node(nid)
            if not node:
                continue
            score = self.score_node_for_model(node, model_name)
            scored.append((score, node))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [n for _, n in scored]