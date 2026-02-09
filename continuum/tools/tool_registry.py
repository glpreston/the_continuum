
from __future__ import annotations

import time

from typing import Dict, Any
from .tool import Tool


class ToolRegistry:
    """
    Registry for all tools available to The Continuum.
    Allows:
      - registering tools
      - retrieving tools by name
      - executing tools safely
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    # ---------------------------------------------------------
    # REGISTRATION
    # ---------------------------------------------------------
    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    # ---------------------------------------------------------
    # RETRIEVAL
    # ---------------------------------------------------------
    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    # ---------------------------------------------------------
    # EXECUTION
    # ---------------------------------------------------------
    def execute(self, name: str, **kwargs: Any) -> Any:
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found.")
        return tool.run(**kwargs)

    # ---------------------------------------------------------
    # LISTING
    # ---------------------------------------------------------
    def list_tools(self) -> Dict[str, str]:
        return {name: tool.description for name, tool in self._tools.items()}
    
    # ---------------------------------------------------------
    # EXECUTION WITH LOGGING
    # ---------------------------------------------------------
    def execute(self, name: str, controller=None, **kwargs: Any) -> Any:
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found.")

        start = time.time()
        error = None
        result = None

        try:
            result = tool.run(**kwargs)
            return result
        except Exception as e:
            error = str(e)
            raise
        finally:
            if controller:
                controller.tool_logs.append({
                    "tool": name,
                    "params": kwargs,
                    "result": result,
                    "error": error,
                    "timestamp": time.time(),
                    "duration": time.time() - start,
                })    