# continuum/orchestrator/controller/controller_telemetry.py

from continuum.core.logger import log_info, log_error
from continuum.telemetry.telemetry_config import TelemetryConfigLoader
from continuum.telemetry.node_health_store import NodeHealthStore
from continuum.telemetry.heartbeat_manager import HeartbeatManager


def initialize_telemetry(controller):
    """
    Phase‑5 telemetry bootstrap:
    - Loads telemetry config
    - Initializes NodeHealthStore
    - Starts HeartbeatManager
    """

    try:
        telemetry_config = TelemetryConfigLoader(controller.db).load()

        controller.node_health_store = NodeHealthStore(lambda: controller.db)

        controller.heartbeat = HeartbeatManager(
            config=telemetry_config,
            node_store=controller.registry,
            node_health_store=controller.node_health_store,
            db_session_factory=lambda: controller.db,
            logger=controller.logger.info,
        )

        # System start hook
        controller.heartbeat.on_system_start()

        log_info("[Telemetry] HeartbeatManager started (warmup active)", phase="telemetry")

    except Exception as e:
        log_error(f"[Telemetry] Failed to initialize heartbeat: {e}", phase="telemetry")
        controller.heartbeat = None