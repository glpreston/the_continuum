"""
Routing helpers for The Continuum.
This module stays intentionally small and focused.
"""

from __future__ import annotations
from typing import Optional

from .types import Message


def is_tool_call(msg: Message) -> bool:
    """Return True if the message indicates a tool invocation."""
    return msg.role == "tool" or msg.metadata.get("tool") is not None


def is_system_hint(msg: Message) -> bool:
    """Return True if the message is a system-level instruction."""
    return msg.role == "system"


def extract_actor(msg: Message) -> Optional[str]:
    """Return the actor_id if present."""
    return msg.metadata.get("actor_id")