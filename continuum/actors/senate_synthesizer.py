# continuum/actors/senate_synthesizer.py

from continuum.actors.base_actor import BaseActor
from continuum.actors.utils import apply_voiceprint_style
from continuum.persona.voiceprints import VOICEPRINTS
from continuum.persona.actor_cards import ACTOR_CARDS


class SenateSynthesizer(BaseActor):
    name = "senate_synthesizer"

    def __init__(self):
        super().__init__(self.name)
        self.voice = VOICEPRINTS[self.name]
        self.card = ACTOR_CARDS[self.name]

    def propose(self, context, message: str) -> dict:
        raw = (
            f"As the Synthesizer, I integrate multiple perspectives to form a "
            f"coherent whole. I balance structure, narrative, and analysis "
            f"around your message: '{message}'."
        )

        styled = apply_voiceprint_style(raw, self.voice)

        return {
            "actor": self.name,
            "content": styled,
            "confidence": 0.83,
            "metadata": {
                "role": self.card.role_name,
                "essence": self.card.essence,
                "voice": self.voice.ui['label'],
            },
        }

    def summarize_reasoning(self, proposal: dict) -> str:
        return (
            "Integrated multiple viewpoints, resolved tensions, and produced a "
            "balanced, coherent interpretation."
        )

    def respond(self, context, final_proposal: dict) -> str:
        return final_proposal.get("content", "")