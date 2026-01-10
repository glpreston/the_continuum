# continuum/actors/base_actor.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from matplotlib import style

class BaseActor(ABC):
    """
    The foundational actor class for The Continuum.
    Every actor—specialist or meta—derives from this.
    """

    def __init__(self, name: str, persona: Optional[Dict[str, Any]] = None):
        self.name = name
        self.persona = persona or {}

    # ---------------------------------------------------------
    # PROPOSAL GENERATION
    # ---------------------------------------------------------
    def propose(self, context, message: str) -> Dict[str, Any]:
        """
        Default proposal logic.
        Subclasses override this to provide specialized reasoning.
        """
        return {
            "actor": self.name,
            "content": (
                "I acknowledge the message, but I do not yet have "
                "a specialized proposal."
            ),
            "confidence": 0.1,
            "metadata": {
                "type": "default",
                "persona": self.persona,
            },
        }

    # ---------------------------------------------------------
    # FINAL RESPONSE GENERATION
    # ---------------------------------------------------------
    def respond(self, context, selected_proposal: Dict[str, Any]) -> str:
        """
        Converts the selected proposal into a final user-facing response.
        Subclasses may override this to apply persona tone, formatting,
        or additional reasoning.
        """
        return selected_proposal.get("content", "")

    # ---------------------------------------------------------
    # OPTIONAL HOOKS
    # ---------------------------------------------------------
    def load_memory(self, memory_system):
        """
        Optional hook for actors that need memory access.
        """
        self.memory = memory_system

    def load_tools(self, tool_registry):
        """
        Optional hook for actors that need tool access.
        """
        self.tools = tool_registry

    def summarize_reasoning(self, proposal: dict) -> str:
        """
        Safe, abstracted explanation of why this actor proposed what they did.
        Does NOT reveal chain-of-thought. Uses persona traits only.
        """
        persona = self.persona

        style = persona.get("style", "general")
        goal = persona.get("goal", "provide helpful guidance")
    
        return (
            f"This proposal reflects the actor's style of {style}, "
            f"aimed at {goal}. It focuses on the key elements the actor "
            f"considers most relevant to the user's message."
        )