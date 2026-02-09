"""
Tool registry for The Continuum.
Allows dynamic discovery and invocation of tools.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any

from continuum.tools.tool_interface import Tool


@dataclass
class ToolRegistry:
    """Stores and retrieves tools by name."""
    tools: Dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        """Add a tool to the registry."""
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Retrieve a tool by name."""
        return self.tools.get(name)

    def run(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a registered tool."""
        tool = self.get(name)
        if not tool:
            return {"error": f"Tool '{name}' not found."}
        return tool.run(**kwargs)