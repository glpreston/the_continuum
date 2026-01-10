"""
Episodic memory: stores recent experiences and interactions.
Useful for short‑term continuity and contextual reasoning.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

from continuum.memory.memory_store import MemoryStore
from continuum.core.context import ContinuumContext


@dataclass
class EpisodicMemory:
    store: MemoryStore

    def record(self, context: ContinuumContext) -> None:
        """Save the latest user message as an episodic entry."""
        msg = context.last_user_message()
        if not msg:
            return

        entry: Dict[str, Any] = {
            "content": msg.content,
            "metadata": msg.metadata,
        }
        self.store.add_episode(entry)

    def recall_recent(self, limit: int = 5):
        """Return the most recent episodic entries."""
        return self.store.recent_episodes(limit)