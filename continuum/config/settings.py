"""
Continuum configuration settings.
Defines model defaults and system‑level behavior flags.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ModelConfig:
    """Configuration for a single language model backend."""
    name: str
    provider: str
    temperature: float = 0.7
    max_tokens: int = 2048
    extra: Dict[str, Any] | None = None


@dataclass
class ContinuumSettings:
    """Top‑level configuration for The Continuum."""
    default_model: ModelConfig
    senate_size: int = 5
    jury_size: int = 3
    enable_memory: bool = True
    enable_tools: bool = True
    debug: bool = False


DEFAULT_SETTINGS = ContinuumSettings(
    default_model=ModelConfig(
        name="continuum-primary",
        provider="openai-like",
        temperature=0.65,
        max_tokens=4096,
    ),
    senate_size=5,
    jury_size=3,
    enable_memory=True,
    enable_tools=True,
    debug=True,
)