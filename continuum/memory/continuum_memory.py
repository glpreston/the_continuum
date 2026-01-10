from __future__ import annotations
from typing import Any, Dict, List, Optional
from .memory_record import MemoryRecord


class ContinuumMemory:
    """
    A simple key-value memory store for The Continuum.
    Supports:
      - adding memories
      - retrieving by key
      - searching by substring
      - snapshotting for context
    """

    def __init__(self):
        self._store: Dict[str, MemoryRecord] = {}

    # ---------------------------------------------------------
    # ADD / UPDATE
    # ---------------------------------------------------------
    def add(self, key: str, value: Any, **metadata: Any) -> None:
        self._store[key] = MemoryRecord(
            key=key,
            value=value,
            metadata=metadata,
        )

    # ---------------------------------------------------------
    # RETRIEVE
    # ---------------------------------------------------------
    def get(self, key: str) -> Optional[Any]:
        record = self._store.get(key)
        return record.value if record else None

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------
    def search(self, query: str) -> List[MemoryRecord]:
        query_lower = query.lower()
        return [
            record
            for record in self._store.values()
            if query_lower in record.key.lower()
            or query_lower in str(record.value).lower()
        ]

    # ---------------------------------------------------------
    # SNAPSHOT
    # ---------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {key: record.value for key, record in self._store.items()}