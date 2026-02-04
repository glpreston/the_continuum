# Copyright 2023 The Continuum Authors. All rights reserved.
# continuum/actors/telemetry/probe_result.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class ProbeResult:
    node_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    latency_ms: Optional[float] = None
    success: bool = False
    status_code: Optional[int] = None
    error_message: Optional[str] = None

    @staticmethod
    def success_result(node_id: int, latency_ms: float) -> "ProbeResult":
        return ProbeResult(
            node_id=node_id,
            timestamp=datetime.utcnow(),
            latency_ms=latency_ms,
            success=True,
            status_code=200,
            error_message=None,
        )


    @staticmethod
    def success_result(
        node_id: int,
        status_code: int = 200,
        latency_ms: float = None,
    ) -> "ProbeResult":
        return ProbeResult(
            node_id=node_id,
            timestamp=datetime.utcnow(),
            latency_ms=latency_ms,
            success=True,
            status_code=status_code,
            error_message=None,
        )