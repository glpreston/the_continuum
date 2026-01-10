# continuum/actors/senate_storyweaver.py

from continuum.actors.base_actor import BaseActor
from continuum.actors.utils import apply_voiceprint_style
from continuum.persona.voiceprints import VOICEPRINTS
from continuum.persona.actor_cards import ACTOR_CARDS


class SenateStoryweaver(BaseActor):
    name = "senate_storyweaver"

    def __init__(self):
        super().__init__(self.name)
        self.voice = VOICEPRINTS[self.name]
        self.card = ACTOR_CARDS[self.name]
        
    def propose(self, context, message: str) -> dict:
        raw = (
            f"As the Storyweaver, I interpret your message as a narrative arc. "
            f"It contains a beginning, tension, and a direction for resolution. "
            f"Your message was: '{message}'."
        )

        styled = apply_voiceprint_style(raw, self.voice)

        return {
            "actor": self.name,
            "content": styled,
            "confidence": 0.80,
            "metadata": {
                "role": self.card.role_name,
                "essence": self.card.essence,
                "voice": self.voice.ui['label'],
            },
        }

    def summarize_reasoning(self, proposal: dict) -> str:
        return (
            "Framed the request as a narrative, identified emotional and symbolic "
            "patterns, and highlighted intuitive meaning."
        )

    def respond(self, context, final_proposal: dict) -> str:
        return final_proposal.get("content", "")