# continuum/monitoring/heartbeat.py

import time
import requests
from datetime import datetime

from continuum.db.sqlalchemy_connection import get_db_session
from continuum.db.models.nodes import Node, NodeStatus
from continuum.db.models.node_health import NodeHealth

# NEW: imports for degraded-node refresh
from continuum.config.model_search import refresh_node
from continuum.db.mysql_connection import db_pool
from continuum.core.logger import log_info, log_debug, log_error


def handle_degraded_node(node):
    """Trigger a model refresh when a node becomes degraded."""
    try:
        log_info(f"[ModelSync] Node {node.host} degraded — triggering model refresh", phase="heartbeat")
        refresh_node(node_id=node.id, endpoint=node.host, db_pool=db_pool)
    except Exception as e:
        log_error(f"[ModelSync] Failed degraded-node refresh: {e}", phase="heartbeat")


def heartbeat_loop(interval_seconds: int = 10):
    """
    Periodically pings all enabled nodes and records:
    - latency
    - online/offline status
    - timestamp
    """

    while True:
        db = get_db_session()
        nodes = db.query(Node).filter(Node.enabled == True).all()

        for node in nodes:
            start = time.time()

            try:
                # Ping the node's health endpoint
                url = f"http://{node.host}/api/tags"
                r = requests.get(url, timeout=2)

                latency = int((time.time() - start) * 1000)
                status = NodeStatus.online if r.status_code == 200 else NodeStatus.unknown

            except Exception:
                latency = None
                status = NodeStatus.offline

            # Compute a simple health score
            if status == NodeStatus.offline:
                health_score = 0.0
            elif latency is None:
                health_score = 0.2
            elif latency > 1000:
                health_score = 0.3
            elif latency > 500:
                health_score = 0.5
            else:
                health_score = 1.0

            # Trigger degraded-node refresh
            if health_score < 0.5:
                handle_degraded_node(node)

            # Write a health record
            record = NodeHealth(
                node_id=node.id,
                timestamp=datetime.utcnow(),
                latency_ms=latency,
                status=status.value
            )
            db.add(record)

            # Update node status + last_seen
            node.status = status
            node.last_seen = datetime.utcnow()

        db.commit()
        db.close()

        time.sleep(interval_seconds)