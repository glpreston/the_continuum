# continuum/actors/senate_architect.py

from continuum.actors.base_actor import BaseActor
from continuum.actors.utils import apply_voiceprint_style
from continuum.persona.voiceprints import VOICEPRINTS
from continuum.persona.actor_cards import ACTOR_CARDS


class SenateArchitect(BaseActor):
    name = "senate_architect"

    def __init__(self):
        super().__init__(self.name)
        self.voice = VOICEPRINTS[self.name]
        self.card = ACTOR_CARDS[self.name]
        
    # ---------------------------------------------------------
    # PROPOSAL GENERATION
    # ---------------------------------------------------------
    def propose(self, context, message: str) -> dict:
        raw = (
            f"As the Architect, I will analyze the structure of your request. "
            f"We can break this into components, define relationships, and "
            f"outline a coherent framework. Your message was: '{message}'."
        )

        styled = apply_voiceprint_style(raw, self.voice)

        return {
            "actor": self.name,
            "content": styled,
            "confidence": 0.85,
            "metadata": {
                "role": self.card.role_name,
                "essence": self.card.essence,
                "voice": self.voice.ui["label"],
            },
        }

    # ---------------------------------------------------------
    # REASONING SUMMARY (J9)
    # ---------------------------------------------------------
    def summarize_reasoning(self, proposal: dict) -> str:
        return (
            "Identified structural components, clarified relationships, "
            "and proposed a stable conceptual framework."
        )

    # ---------------------------------------------------------
    # FINAL RESPONSE
    # ---------------------------------------------------------
    def respond(self, context, final_proposal: dict) -> str:
        return final_proposal.get("content", "")