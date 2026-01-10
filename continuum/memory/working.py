"""
Working memory: short‑term scratchpad for the current turn.
Used for intermediate reasoning or temporary values.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class WorkingMemory:
    """Temporary memory that resets each turn."""
    data: Dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def clear(self) -> None:
        self.data.clear()