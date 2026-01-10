"""
Shared foundational types for The Continuum.
These dataclasses define the structure of messages,
deliberation steps, and orchestration results.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

Role = Literal["user", "assistant", "system", "actor", "tool"]


@dataclass
class Message:
    role: Role
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeliberationStep:
    actor_id: str
    reasoning: str
    proposal: str
    weight: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    final_response: str
    steps: List[DeliberationStep]
    debug_info: Dict[str, Any] = field(default_factory=dict)