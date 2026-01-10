"""
Adapter layer that plugs the MySQL backend into the existing
EpisodicMemory and SemanticMemory classes.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from continuum.memory.mysql_backend import MySQLMemoryBackend
from continuum.core.context import ContinuumContext


@dataclass
class MySQLEpisodicMemory:
    backend: MySQLMemoryBackend

    def record(self, context: ContinuumContext) -> None:
        msg = context.last_user_message()
        if not msg:
            return

        entry: Dict[str, Any] = {
            "content": msg.content,
            "metadata": msg.metadata,
        }
        self.backend.add_episode(entry)

    def recall_recent(self, limit: int = 5):
        return self.backend.recent_episodes(limit)


@dataclass
class MySQLSemanticMemory:
    backend: MySQLMemoryBackend

    def set(self, key: str, value: Any) -> None:
        self.backend.add_semantic(key, value)

    def get(self, key: str) -> Any:
        return self.backend.get_semantic(key)

    def merge_into_context(self, context: ContinuumContext) -> None:
        # Load all semantic memory into context snapshot
        # (Optional: add a method to backend to fetch all)
        pass