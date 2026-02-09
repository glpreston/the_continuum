# continuum/telemetry/node_health_store.py

from datetime import datetime
from sqlalchemy.orm import Session
from continuum.db.models.node_health import NodeHealth
from continuum.db.models.nodes import Node


class NodeHealthStore:
    """
    Provides a clean API for reading and writing node health data.
    All DB interactions for the telemetry subsystem flow through here.

    IMPORTANT (Phase‑5):
    - This class no longer creates its own SQLAlchemy sessions.
    - All methods now accept a `session` parameter.
    - This allows the heartbeat thread to use its own session safely.
    """

    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    # ---------------------------------------------------------
    # Ensure a row exists for a node (one row per node enforced)
    # ---------------------------------------------------------
    def ensure_row(self, node_id: int, session: Session):
        row = session.query(NodeHealth).filter_by(node_id=node_id).first()
        if row is None:
            row = NodeHealth(node_id=node_id)
            session.add(row)
        return row

    # ---------------------------------------------------------
    # Fetch health row for a node
    # ---------------------------------------------------------
    def get(self, node_id: int, session: Session):
        return session.query(NodeHealth).filter_by(node_id=node_id).first()

    # ---------------------------------------------------------
    # Fetch all node health rows
    # ---------------------------------------------------------
    def get_all(self, session: Session):
        return session.query(NodeHealth).all()

    # ---------------------------------------------------------
    # Fetch all non-quarantined nodes (for routing)
    # ---------------------------------------------------------
    def get_all_healthy(self, session: Session):
        return (
            session.query(NodeHealth)
            .filter_by(quarantined=0)
            .order_by(NodeHealth.health_score.desc())
            .all()
        )

    # ---------------------------------------------------------
    # Update node health from a probe result + scoring result
    # ---------------------------------------------------------
    def update_from_probe(self, node_id: int, probe, scoring_result, session: Session):
        """
        probe: ProbeResult object
        scoring_result: HealthScoreResult object

        NOTE:
        - Session is provided by caller (thread-safe).
        - Caller is responsible for commit/rollback.
        """

        row = session.query(NodeHealth).filter_by(node_id=node_id).first()

        if row is None:
            row = NodeHealth(node_id=node_id)
            session.add(row)

        # Update heartbeat timestamp
        row.last_heartbeat_at = datetime.utcnow()
        row.updated_at = datetime.utcnow()

        # Latency + status
        row.latency_ms = probe.latency_ms
        row.status = scoring_result.status

        # Streaks + counters
        row.failure_count = scoring_result.failure_count
        row.success_count = scoring_result.success_count
        row.failure_streak = scoring_result.failure_streak
        row.success_streak = scoring_result.success_streak

        # Scoring + quarantine
        row.health_score = scoring_result.health_score
        row.quarantined = 1 if scoring_result.quarantined else 0

        # Error message
        row.last_error = probe.error_message

        # No commit here — caller handles it.

    # ---------------------------------------------------------
    # Mark a node as quarantined
    # ---------------------------------------------------------
    def quarantine(self, node_id: int, session: Session):
        row = session.query(NodeHealth).filter_by(node_id=node_id).first()
        if row:
            row.quarantined = 1
            row.updated_at = datetime.utcnow()

    # ---------------------------------------------------------
    # Mark a node as recovered
    # ---------------------------------------------------------
    def recover(self, node_id: int, session: Session):
        row = session.query(NodeHealth).filter_by(node_id=node_id).first()
        if row:
            row.quarantined = 0
            row.updated_at = datetime.utcnow()