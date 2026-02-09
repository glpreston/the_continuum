# continuum/telemetry/heartbeat_manager.py

import threading
import time
from datetime import datetime, timedelta
from enum import Enum

from continuum.telemetry.node_probe import NodeProbe
from continuum.telemetry.health_scoring import HealthScoringEngine
from continuum.telemetry.node_health_store import NodeHealthStore


class HeartbeatState(Enum):
    STARTUP_WARMUP = "startup_warmup"
    ACTIVE_MONITORING = "active_monitoring"
    IDLE = "idle"


class HeartbeatManager:
    """
    Orchestrates the telemetry heartbeat lifecycle:
    - Startup warmup (always runs for X minutes)
    - Event-driven activation on user prompts
    - Idle shutdown after inactivity
    """

    def __init__(
        self,
        config,
        node_store,
        node_health_store: NodeHealthStore,
        db_session_factory,
        logger=None
    ):
        self.config = config
        self.node_store = node_store
        self.node_health_store = node_health_store
        self.db_session_factory = db_session_factory

        self.logger = logger or print

        self.state = HeartbeatState.STARTUP_WARMUP
        self.thread = None
        self.stop_event = threading.Event()

        self.last_activity = datetime.utcnow()
        self.warmup_end_time = datetime.utcnow() + timedelta(
            minutes=self.config.startup_warmup_minutes
        )

        self.probe = NodeProbe()
        self.scoring = HealthScoringEngine(config)

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------
    def on_system_start(self):
        self.logger("Heartbeat: system start → entering STARTUP_WARMUP")
        self._start_thread()

    def on_user_prompt(self):
        self.last_activity = datetime.utcnow()

        if self.state == HeartbeatState.IDLE:
            self.logger("Heartbeat: user activity detected → ACTIVE_MONITORING")
            self.state = HeartbeatState.ACTIVE_MONITORING
            self._start_thread()

    def stop(self):
        self.logger("Heartbeat: stopping")
        self.stop_event.set()
        if self.thread:
            self.thread.join()

    # ---------------------------------------------------------
    # Internal thread management
    # ---------------------------------------------------------
    def _start_thread(self):
        if self.thread and self.thread.is_alive():
            return

        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    # ---------------------------------------------------------
    # Main heartbeat loop
    # ---------------------------------------------------------
    def _run_loop(self):
        while not self.stop_event.is_set():
            now = datetime.utcnow()

            # ---------------------------------------------
            # State transitions
            # ---------------------------------------------
            if self.state == HeartbeatState.STARTUP_WARMUP:
                if now >= self.warmup_end_time:
                    if self._recent_activity():
                        self.logger("Heartbeat: warmup complete → ACTIVE_MONITORING")
                        self.state = HeartbeatState.ACTIVE_MONITORING
                    else:
                        self.logger("Heartbeat: warmup complete → IDLE")
                        self.state = HeartbeatState.IDLE
                        break

            elif self.state == HeartbeatState.ACTIVE_MONITORING:
                if not self._recent_activity():
                    self.logger("Heartbeat: idle timeout → IDLE")
                    self.state = HeartbeatState.IDLE
                    break

            elif self.state == HeartbeatState.IDLE:
                break

            # ---------------------------------------------
            # Perform heartbeat
            # ---------------------------------------------
            self._probe_all_nodes()

            # ---------------------------------------------
            # Sleep until next interval
            # ---------------------------------------------
            time.sleep(self.config.heartbeat_interval_seconds)

    # ---------------------------------------------------------
    # Probe all nodes and update DB (thread-safe)
    # ---------------------------------------------------------
    def _probe_all_nodes(self):
        """
        Each heartbeat iteration uses its own SQLAlchemy session.
        This prevents cross-thread session reuse and packet sequence errors.
        """
        nodes = self.node_store.get_all_nodes()

        for node in nodes:
            session = self.db_session_factory()

            try:
                probe_result = self.probe.probe(node)

                previous = self.node_health_store.get(node.id, session=session)
                scoring_result = self.scoring.score(probe_result, previous)

                self.node_health_store.update_from_probe(
                    node_id=node.id,
                    probe=probe_result,
                    scoring_result=scoring_result,
                    session=session,
                )

                session.commit()

            except Exception as e:
                session.rollback()
                self.logger(f"[Heartbeat] DB error during probe: {e}")

            finally:
                session.close()

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    def _recent_activity(self):
        age = (datetime.utcnow() - self.last_activity).total_seconds()
        return age < (self.config.idle_timeout_minutes * 60)