# continuum/telemetry/node_probe.py

import time
import requests
from requests.exceptions import RequestException
from continuum.telemetry.probe_result import ProbeResult
from continuum.config.model_search import refresh_node
from continuum.core.logger import log_info, log_debug, log_error

# from continuum.db.mysql_connection import db_pool

class NodeProbe:
    """
    Performs a /health (or fallback) probe against a node.
    Measures latency and returns a ProbeResult.
    """

    def __init__(self, timeout_seconds=3):
        self.timeout_seconds = timeout_seconds

    # ---------------------------------------------------------
    # Probe a single node
    # ---------------------------------------------------------
    def probe(self, node) -> ProbeResult:
        """
        node: Node ORM object with fields:
              - id
              - host (base URL, e.g. http://localhost:11434)
        """

        base = node.host.rstrip("/")

        # Preferred endpoints in order
        endpoints = [
            f"{base}/api/tags",
            f"{base}/version",
        ]

        for url in endpoints:
            result = self._try_probe(node, url)
            if result is not None:
                return result

        # If all endpoints fail, return failure
        return ProbeResult.failure_result(
            node_id=node.id,
            error_message="All probe endpoints failed"
        )

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _try_probe(self, node, url):
        start = time.perf_counter()

        try:
            response = requests.get(url, timeout=self.timeout_seconds)
            latency_ms = (time.perf_counter() - start) * 1000.0

            if response.status_code == 200:
                return ProbeResult.success_result(
                    node_id=node.id,
                    latency_ms=latency_ms,
                    status_code=response.status_code,
                )
            else:
                return ProbeResult.failure_result(
                    node_id=node.id,
                    error_message=f"HTTP {response.status_code}",
                    status_code=response.status_code,
                )

        except RequestException:
            return None  # try next endpoint
        
    def handle_degraded_node(node):
        try:
            log_info(f"[ModelSync] Node {node['hostname']} degraded — triggering refresh", phase="model_sync")
            #refresh_node(node_id=node["id"], endpoint=node["endpoint"], db_pool=db_pool)
            refresh_node(node_id=node["id"], endpoint=node["endpoint"])

        except Exception as e:
            log_debug(f"[ModelSync] Failed degraded-node refresh: {e}", phase="model_sync")
