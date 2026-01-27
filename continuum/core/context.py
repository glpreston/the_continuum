
# continuum/core/context.py

"""
Conversation context for The Continuum.
Tracks messages, memory snapshots, and user profile data.
"""

from __future__ import annotations
import inspect
import traceback

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

    # Phase‑4 emotional fields
    emotional_state: Any = None
    emotional_memory: Any = None

    def add(self, role: str, content: str, **meta: Any) -> None:
        """Append a new message to the conversation."""
        self.messages.append(Message(role=role, content=content, metadata=meta))

    def add_user_message(self, content: str) -> None:
        self.add("user", content)

    #def add_assistant_message(self, content: str) -> None:
        #self.add("assistant", content)
        #print("ADD_ASSISTANT_MESSAGE CALLED:", content[:50])

    def add_assistant_message(self, content: str) -> None:
        self.add("assistant", content)

        print("\n================ ASSISTANT MESSAGE DEBUG ================")
        print("CONTENT PREVIEW:", repr(content[:200]))
        print("TYPE:", type(content))

        # Who called this function?
        stack = traceback.extract_stack(limit=5)
        print("CALL STACK:")
        for frame in stack:
            print(f"  - {frame.filename}:{frame.lineno} in {frame.name}")

        # Which module invoked it?
        caller = inspect.stack()[1]
        print("CALLER MODULE:", caller.frame.f_globals.get("__name__"))

        print("=========================================================\n")



    def last_user_message(self) -> Optional[Message]:
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg
        return None

    def history(self) -> List[Message]:
        return self.messages

    def get_text_window(self, n: int = 8) -> str:
        """Return the last n messages as plain text for prompt templates."""
        return "\n".join([m.content for m in self.messages[-n:]])

    def get_memory_summary(self) -> str:
        """Return a compact summary of semantic memory, or empty string."""
        if not hasattr(self, "memory") or not self.memory:
            return ""
        if hasattr(self.memory, "semantic") and self.memory.semantic:
            keys = list(self.memory.semantic.keys())
            return "Semantic memory keys: " + ", ".join(keys[:5])
        return ""