"""
Tool interface for The Continuum.
Each tool exposes a simple `run` method and a short description.
"""

from __future__ import annotations
from typing import Protocol, Any, Dict


class Tool(Protocol):
    """Base protocol for all Continuum tools."""

    name: str
    description: str

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the tool with keyword arguments.
        Returns a dictionary with structured results.
        """
        ...