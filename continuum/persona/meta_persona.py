from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class MetaPersona:
    """
    The unified voice of The Continuum.
    Transforms actor output into a coherent, emotionally aware response.
    """

    name: str
    voice: str
    traits: Dict[str, str]

    def render(self, actor_output: str, context: Any) -> str:
        prefix = ""

        # Show meta-persona prefix
        if context.debug_flags.get("show_meta_persona"):
            prefix += f"{self.name}: "

        # Show winning actor name
        if context.debug_flags.get("show_actor_name") and context.last_final_proposal:
            actor = context.last_final_proposal.get("actor", "unknown")
            prefix += f"[{actor}] "

        # For now, we return the raw output with optional prefixes.
        # Later we can add tone shaping, rewriting, etc.
        return f"{prefix}{actor_output}"