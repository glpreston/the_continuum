from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict


class Tool(ABC):
    """
    Base class for all tools in The Continuum.
    Tools expose a simple `run` method and metadata.
    """

    name: str = "unnamed_tool"
    description: str = "No description provided."

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """Execute the tool with the given parameters."""
        raise NotImplementedError