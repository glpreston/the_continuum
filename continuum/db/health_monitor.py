# continuum/db/health_monitor.py

import threading
import time
import requests
from datetime import datetime
from sqlalchemy.orm import Session

from continuum.db.models.nodes import Node, NodeStatus
from continuum.db.models.node_health import NodeHealth, HealthStatus
from continuum.db.registry import ModelRegistry


class HealthMonitor(threading.Thread):
    """
    Background thread that continuously checks the health of all nodes.
    Updates:
    - node.status
    - node.last_seen
    - node_health history
    - registry state
    """

    def __init__(
        self,
        db_session: Session,
        registry: ModelRegistry,
        interval_seconds: int = 5,
        timeout_seconds: int = 2,
    ):
        super().__init__(daemon=True)
        self.db = db_session
        self.registry = registry
        self.interval = interval_seconds
        self.timeout = timeout_seconds
        self.running = True

    # ---------------------------------------------------------
    # PING OLLAMA NODE
    # ---------------------------------------------------------
    def _ping_ollama(self, node: Node) -> int:
        """
        Returns latency in ms or -1 if unreachable.
        """
        try:
            start = time.time()
            url = f"{node.host}/api/version"
            requests.get(url, timeout=self.timeout)
            end = time.time()
            return int((end - start) * 1000)
        except Exception:
            return -1

    # ---------------------------------------------------------
    # PING CLOUD NODE
    # ---------------------------------------------------------
    def _ping_cloud(self, node: Node) -> int:
        """
        Cloud nodes vary by provider.
        For now, we simply attempt a trivial request.
        """
        try:
            start = time.time()

            # Placeholder: cloud providers will have their own ping endpoints
            # For now, we simulate a simple GET to the host
            requests.get(node.host, timeout=self.timeout)

            end = time.time()
            return int((end - start) * 1000)
        except Exception:
            return -1

    # ---------------------------------------------------------
    # CHECK NODE HEALTH
    # ---------------------------------------------------------
    def check_node(self, node: Node):
        """
        Ping a node, update DB, update registry.
        """
        if node.type.value == "ollama":
            latency = self._ping_ollama(node)
        else:
            latency = self._ping_cloud(node)

        # Determine status
        if latency == -1:
            status = NodeStatus.offline
            health_status = HealthStatus.offline
        elif latency > 1000:
            status = NodeStatus.online
            health_status = HealthStatus.degraded
        else:
            status = NodeStatus.online
            health_status = HealthStatus.online

        # Update node record
        node.status = status
        node.last_seen = datetime.utcnow()

        # Insert health history
        record = NodeHealth(
            node_id=node.id,
            latency_ms=latency if latency != -1 else None,
            status=health_status,
        )
        self.db.add(record)

        self.db.commit()

    # ---------------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------------
    def run(self):
        while self.running:
            # Refresh registry in case nodes/models changed
            self.registry.refresh()

            for node in self.registry.nodes:
                if not node.enabled:
                    continue
                self.check_node(node)

            time.sleep(self.interval)

    # ---------------------------------------------------------
    # STOP MONITOR
    # ---------------------------------------------------------
    def stop(self):
        self.running = False