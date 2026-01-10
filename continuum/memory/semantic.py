"""
Semantic memory: stores stable facts about the user or system.
Examples: preferences, long‑term goals, known facts.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from continuum.memory.memory_store import MemoryStore


@dataclass
class SemanticMemory:
    store: MemoryStore

    def set(self, key: str, value: Any) -> None:
        """Store or update a semantic fact."""
        self.store.add_semantic(key, value)

    def get(self, key: str) -> Any:
        """Retrieve a semantic fact."""
        return self.store.get_semantic(key)

    def merge_into_context(self, context) -> None:
        """Inject semantic memory into the context snapshot."""
        context.memory_snapshot.update(self.store.semantic)