#  continuum/db/registry/performance_scoring.py

from continuum.db.models.model_stats import ModelStats


class PerformanceScoringMixin:
    """
    Computes performance score based on model_stats.
    NOTE: current schema has no node_id, so stats are global per model.
    """

    def evaluate_node_performance(self, node, model_name):
        stats = (
            self.db.query(ModelStats)
            .filter(ModelStats.model_name == model_name)
            .first()
        )

        if not stats:
            return 0.5

        score = 1.0

        # Success rate
        if stats.success_rate is not None:
            score *= stats.success_rate

        # Latency
        if stats.avg_latency_ms:
            if stats.avg_latency_ms < 500:
                score *= 1.0
            elif stats.avg_latency_ms < 1500:
                score *= 0.7
            else:
                score *= 0.4

        return max(0.0, min(1.0, score))