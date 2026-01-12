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
        # 1. Generate reasoning steps
        steps = self.reason(context, message)

        # 2. Generate proposal content from reasoning
        raw = self.generate_proposal_from_steps(steps, message)

        # 3. Apply voiceprint styling
        styled = apply_voiceprint_style(raw, self.voice)

        # 4. Compute dynamic confidence
        confidence = self.compute_confidence(steps)

        return {
            "actor": self.name,
            "content": styled,
            "confidence": confidence,
            "metadata": {
                "role": self.card.role_name,
                "essence": self.card.essence,
                "voice": self.voice.ui['label'],
                "reasoning": steps,
            },
        }

    def summarize_reasoning(self, proposal: dict) -> str:
        return (
            "Framed the request as a narrative, identified emotional and symbolic "
            "patterns, and highlighted intuitive meaning."
            )
    
    def respond(self, context, final_proposal: dict) -> str:
        return final_proposal.get("content", "")
    
    def speak_proposal(self, proposal_text: str):
        return self.speak(proposal_text)
        
    def reason(self, context, message: str) -> list:
        """
        Storyweaver-specific multi-step reasoning.
        Focuses on narrative arc, imagery, and emotional tone.
        """
        return [
            "Step 1: Sense the emotional tone and intention behind the user's message.",
            "Step 2: Choose a narrative frame or setting that matches the tone.",
            "Step 3: Select imagery, metaphors, and emotional textures.",
            "Step 4: Shape the narrative arc with tension and resolution.",
            "Step 5: Deliver a cohesive, warm, imaginative story."
        ]

    def generate_proposal_from_steps(self, steps: list, message: str) -> str:
        """
        Storyweaver proposal: warm, imaginative, emotionally resonant.
        Integrates reasoning steps into a narrative-style response that
        directly addresses the user's message.
        """

        # 1. Actor-specific framing
        intro = (
            "Warm in approach, as the Storyweaver, I understand your request "
            "through imagery, emotional tone, and the arc of a story waiting to unfold."
        )

        # 2. Message interpretation
        interpretation = (
            f"Your message asks: '{message}'. I interpret this as an invitation "
            "to shape meaning through metaphor, emotion, and symbolic clarity."
        )

        # 3. Reasoning integration
        reasoning_summary = (
            "Following my reasoning steps, I begin by sensing the emotional tone, "
            "then choose a narrative frame, select imagery that resonates, shape "
            "the arc with tension and release, and finally express the insight "
            "through a cohesive and evocative story."
        )

        # 4. Actor-specific narrative output
        narrative = (
            "Here is the narrative interpretation:\n"
            "- **Emotional Undercurrent:** Identify the feeling that anchors the request.\n"
            "- **Symbolic Imagery:** Choose metaphors or scenes that reflect the theme.\n"
            "- **Arc of Meaning:** Shape a beginning, tension, and resolution.\n"
            "- **Emotional Insight:** Reveal the deeper message carried by the imagery.\n"
            "- **Closing Gesture:** Leave the reader with a resonant emotional impression."
        )

        # 5. Persona-aligned closing
        closing = (
            "This story-shaped interpretation reflects an intuitive and emotionally "
            "attuned reading of your request."
        )

        return f"{intro}\n\n{interpretation}\n\n{reasoning_summary}\n\n{narrative}\n\n{closing}"
        
    def compute_confidence(self, steps: list) -> float:
        """
        Storyweaver confidence grows with emotional clarity and narrative cohesion.
        Slightly lower base to avoid overpowering technical actors.
        """
        base = 0.76
        bonus = min(len(steps) * 0.03, 0.15)
        return round(base + bonus, 3)                        