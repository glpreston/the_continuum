"""
Utility helpers for creating structured messages.
Keeps message creation consistent across the system.
"""

from __future__ import annotations
from typing import Any, Dict

from .types import Message


def user_message(content: str, **meta: Any) -> Message:
    return Message(role="user", content=content, metadata=meta)


def assistant_message(content: str, **meta: Any) -> Message:
    return Message(role="assistant", content=content, metadata=meta)


def system_message(content: str, **meta: Any) -> Message:
    return Message(role="system", content=content, metadata=meta)


def actor_message(actor_id: str, content: str, **meta: Any) -> Message:
    meta = {"actor_id": actor_id, **meta}
    return Message(role="actor", content=content, metadata=meta)