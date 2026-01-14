"""
Conversation context for The Continuum.
Tracks messages, memory snapshots, and user profile data.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .types import Message
from continuum.memory.continuum_memory import ContinuumMemory

@dataclass
class ContinuumContext:
    conversation_id: str
    messages: List[Message] = field(default_factory=list)
    memory_snapshot: Dict[str, Any] = field(default_factory=dict)
    user_profile: Dict[str, Any] = field(default_factory=dict)
    debug_flags: Dict[str, bool] = field(default_factory=dict)
    memory: ContinuumMemory = field(default_factory=ContinuumMemory)

    def add(self, role: str, content: str, **meta: Any) -> None:
        """Append a new message to the conversation."""
        self.messages.append(Message(role=role, content=content, metadata=meta))

    # ---------------------------------------------------------
    # Convenience wrappers expected by the controller
    # ---------------------------------------------------------
    def add_user_message(self, content: str) -> None:
        self.add("user", content)

    def add_assistant_message(self, content: str) -> None:
        self.add("assistant", content)
        print("ADD_ASSISTANT_MESSAGE CALLED:", content[:50])
    # ---------------------------------------------------------
    # Accessors
    # ---------------------------------------------------------
    def last_user_message(self) -> Optional[Message]:
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg
        return None

    def history(self) -> List[Message]:
        return self.messages

    def get_memory_summary(self) -> str:
        """Return a compact summary of semantic memory, or empty string."""
        if not hasattr(self, "memory") or not self.memory:
            return ""
        if hasattr(self.memory, "semantic") and self.memory.semantic:
            keys = list(self.memory.semantic.keys())
            return "Semantic memory keys: " + ", ".join(keys[:5])
        return ""