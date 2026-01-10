"""
Simple in‑memory storage backend for The Continuum.
This keeps memory logic decoupled from storage implementation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class MemoryStore:
    """A lightweight key‑value store for episodic and semantic memory."""
    episodic: List[Dict[str, Any]] = field(default_factory=list)
    semantic: Dict[str, Any] = field(default_factory=dict)

    def add_episode(self, data: Dict[str, Any]) -> None:
        self.episodic.append(data)

    def add_semantic(self, key: str, value: Any) -> None:
        self.semantic[key] = value

    def get_semantic(self, key: str) -> Any:
        return self.semantic.get(key)

    def recent_episodes(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self.episodic[-limit:]