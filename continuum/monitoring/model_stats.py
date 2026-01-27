# continuum/monitoring/model_stats.py

import time
from datetime import datetime

from continuum.db.sqlalchemy_connection import get_db_session
from continuum.db.models.model_stats import ModelStats


def log_model_call(model_name: str, success: bool, latency_ms: int):
    """
    Records a single model call into model_stats.
    Updates:
    - total_calls
    - total_failures
    - success_rate
    - avg_latency_ms
    """

    db = get_db_session()

    stats = (
        db.query(ModelStats)
        .filter(ModelStats.model_name == model_name)
        .first()
    )

    # Create row if missing
    if not stats:
        stats = ModelStats(
            model_name=model_name,
            total_calls=0,
            total_failures=0,
            success_rate=0.0,
            avg_latency_ms=latency_ms,
            last_updated=datetime.utcnow()
        )
        db.add(stats)

    # Update totals
    stats.total_calls += 1
    if not success:
        stats.total_failures += 1

    # Update success rate
    stats.success_rate = (
        (stats.total_calls - stats.total_failures) / stats.total_calls
    )

    # Update average latency (EMA)
    if stats.avg_latency_ms is None:
        stats.avg_latency_ms = latency_ms
    else:
        stats.avg_latency_ms = int(
            (stats.avg_latency_ms * 0.8) + (latency_ms * 0.2)
        )

    stats.last_updated = datetime.utcnow()

    db.commit()
    db.close()