# continuum/monitoring/heartbeat.py

import time
import requests
from datetime import datetime

from continuum.db.sqlalchemy_connection import get_db_session
from continuum.db.models.nodes import Node, NodeStatus
from continuum.db.models.node_health import NodeHealth


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
                url = f"http://{node.host}/health"
                r = requests.get(url, timeout=2)

                latency = int((time.time() - start) * 1000)
                status = NodeStatus.online if r.status_code == 200 else NodeStatus.unknown

            except Exception:
                latency = None
                status = NodeStatus.offline

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