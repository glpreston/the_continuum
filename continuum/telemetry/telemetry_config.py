# telemetry/telemetry_config.py

from dataclasses import dataclass
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker


@dataclass
class TelemetryConfig:
    """
    Strongly-typed configuration object loaded from the telemetry_config table.
    All timing, scoring, and threshold parameters live here.
    """
    heartbeat_interval_seconds: int
    startup_warmup_minutes: int
    idle_timeout_minutes: int

    quarantine_threshold: float
    recovery_threshold: float

    staleness_penalty_seconds: int
    max_latency_ms_for_full_score: int
    max_latency_penalty: float

    failure_streak_penalty_per_failure: float
    max_failure_penalty: float

    success_streak_bonus_per_success: float
    max_success_bonus: float


class TelemetryConfigLoader:
    """
    Loads telemetry configuration from the telemetry_config table.
    Supports both SQLAlchemy Session and sessionmaker.
    """

    def __init__(self, db):
        """
        db can be:
        - a Session instance
        - a sessionmaker
        - a callable returning a Session
        """
        self.db = db

    def _get_session(self) -> Session:
        # Already a Session
        if isinstance(self.db, Session):
            return self.db

        # A sessionmaker instance
        if isinstance(self.db, sessionmaker):
            return self.db()

        # A callable that returns a Session
        if callable(self.db):
            return self.db()

        raise TypeError("db must be a Session, sessionmaker, or callable returning a Session")

    def load(self) -> TelemetryConfig:
        session = self._get_session()

        row = (
            session.execute(
                text(
                    """
                    SELECT
                        heartbeat_interval_seconds,
                        startup_warmup_minutes,
                        idle_timeout_minutes,
                        quarantine_threshold,
                        recovery_threshold,
                        staleness_penalty_seconds,
                        max_latency_ms_for_full_score,
                        max_latency_penalty,
                        failure_streak_penalty_per_failure,
                        max_failure_penalty,
                        success_streak_bonus_per_success,
                        max_success_bonus
                    FROM telemetry_config
                    WHERE id = 1
                    """
                )
            )
            .mappings()
            .first()
        )

        if not row:
            raise RuntimeError("telemetry_config table is empty or missing id=1")

        return TelemetryConfig(**dict(row))