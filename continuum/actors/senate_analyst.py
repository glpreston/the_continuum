# continuum/actors/senate_analyst.py

from continuum.actors.base_actor import BaseActor
from continuum.actors.utils import apply_voiceprint_style
from continuum.persona.voiceprints import VOICEPRINTS
from continuum.persona.actor_cards import ACTOR_CARDS


class SenateAnalyst(BaseActor):
    name = "senate_analyst"

    def __init__(self):
        super().__init__(self.name)
        self.voice = VOICEPRINTS[self.name]
        self.card = ACTOR_CARDS[self.name]

    def propose(self, context, message: str) -> dict:
        raw = (
            f"As the Analyst, I evaluate your request by identifying claims, "
            f"assumptions, and implications. I look for the most consistent "
            f"interpretation. Your message was: '{message}'."
        )

        styled = apply_voiceprint_style(raw, self.voice)

        return {
            "actor": self.name,
            "content": styled,
            "confidence": 0.88,
            "metadata": {
                "role": self.card.role_name,
                "essence": self.card.essence,
                "voice": self.voice.ui['label'],
            },
        }

    def summarize_reasoning(self, proposal: dict) -> str:
        return (
            "Performed logical breakdown, evaluated assumptions, and selected "
            "the most evidence-consistent interpretation."
        )

    def respond(self, context, final_proposal: dict) -> str:
        return final_proposal.get("content", "")