# continuum/telemetry/health_score_result.py

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class HealthScoreResult:
    """
    Represents the computed health state of a node after applying
    scoring logic to a ProbeResult. This is the bridge between the
    scoring engine and the NodeHealthStore.
    """

    node_id: int

    # Final computed score (0.0–1.0)
    health_score: float

    # Node status classification (OK / WARN / FAIL)
    status: str

    # Updated counters
    failure_count: int
    success_count: int

    # Updated streaks
    failure_streak: int
    success_streak: int

    # Whether the node should be quarantined
    quarantined: bool

    # Optional message (e.g., "latency too high", "probe failed")
    reason: Optional[str] = None