# continuum/actors/senate_storyweaver.py

from continuum.actors.base_actor import BaseActor
from continuum.actors.utils import apply_voiceprint_style
from continuum.persona.voiceprints import VOICEPRINTS
from continuum.persona.actor_cards import ACTOR_CARDS
from continuum.emotion.actor_modulation import apply_actor_modulation
from continuum.actors.emotional_hooks import get_emotional_tone


class SenateStoryweaver(BaseActor):
    name = "senate_storyweaver"

    def __init__(self):
        super().__init__(self.name)
        self.voice = VOICEPRINTS[self.name]
        self.card = ACTOR_CARDS[self.name]

    # ---------------------------------------------------------
    # PROPOSAL GENERATION
    # ---------------------------------------------------------
    def propose(self, context, message: str) -> dict:
        controller = getattr(context, "controller", None)
        if controller and hasattr(controller, "emotional_state"):
            modulation = apply_actor_modulation(self.name, controller.emotional_state)
        else:
            modulation = {
                "warmth": 1.0,
                "creativity": 1.0,
                "assertiveness": 1.0,
                "structure": 1.0,
                "verbosity": 1.0,
            }

        steps = self.reason(context, message)
        raw = self.generate_proposal_from_steps(steps, message)

        tone_prefix = (
            f"As the Storyweaver, I shape my voice with:\n"
            f"- Warmth: {modulation['warmth']:.2f}\n"
            f"- Creativity: {modulation['creativity']:.2f}\n"
            f"- Verbosity: {modulation['verbosity']:.2f}\n\n"
        )

        raw = tone_prefix + raw
        styled = apply_voiceprint_style(raw, self.voice)
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
                "modulation": modulation,
            },
        }

    # ---------------------------------------------------------
    # EI‑2.0 Emotional Tone Shaping
    # ---------------------------------------------------------
    def _tone_prefix(self, dominant, confidence, volatility):
        if dominant in ("sadness", "anxiety") and confidence > 0.5:
            return "I can feel the weight in your words. "
        if dominant == "confusion":
            return "Let’s explore this feeling and find the thread together. "
        if volatility > 0.6:
            return "There’s a lot moving beneath the surface — let’s slow down. "
        return ""

    # ---------------------------------------------------------
    # FINAL RESPONSE
    # ---------------------------------------------------------
    def respond(self, context, proposal, emotional_memory, emotional_state):
        tone = get_emotional_tone(emotional_memory, emotional_state)

        dominant = tone["dominant"]
        confidence = tone["confidence"]
        volatility = tone["volatility"]

        prefix = self._tone_prefix(dominant, confidence, volatility)
        return prefix + proposal.get("content", "")

    # ---------------------------------------------------------
    # AUDIO
    # ---------------------------------------------------------
    def speak_proposal(self, proposal_text: str):
        return self.speak(proposal_text)

    # ---------------------------------------------------------
    # MULTI-STEP REASONING
    # ---------------------------------------------------------
    def reason(self, context, message: str) -> list:
        return [
            "Step 1: Sense the emotional tone and intention behind the user's message.",
            "Step 2: Choose a narrative frame or setting that matches the tone.",
            "Step 3: Select imagery, metaphors, and emotional textures.",
            "Step 4: Shape the narrative arc with tension and resolution.",
            "Step 5: Deliver a cohesive, warm, imaginative story.",
        ]

    def generate_proposal_from_steps(self, steps: list, message: str) -> str:
        intro = (
            "Warm in approach, as the Storyweaver, I understand your request "
            "through imagery, emotional tone, and the arc of a story waiting to unfold."
        )

        interpretation = (
            f"Your message asks: '{message}'. I interpret this as an invitation "
            "to shape meaning through metaphor, emotion, and symbolic clarity."
        )

        reasoning_summary = (
            "Following my reasoning steps, I begin by sensing the emotional tone, "
            "then choose a narrative frame, select imagery that resonates, shape "
            "the arc with tension and release, and finally express the insight "
            "through a cohesive and evocative story."
        )

        narrative = (
            "Here is the narrative interpretation:\n"
            "- **Emotional Undercurrent:** Identify the feeling that anchors the request.\n"
            "- **Symbolic Imagery:** Choose metaphors or scenes that reflect the theme.\n"
            "- **Arc of Meaning:** Shape a beginning, tension, and resolution.\n"
            "- **Emotional Insight:** Reveal the deeper message carried by the imagery.\n"
            "- **Closing Gesture:** Leave the reader with a resonant emotional impression."
        )

        closing = (
            "This story-shaped interpretation reflects an intuitive and emotionally "
            "attuned reading of your request."
        )

        return f"{intro}\n\n{interpretation}\n\n{reasoning_summary}\n\n{narrative}\n\n{closing}"

    def compute_confidence(self, steps: list) -> float:
        base = 0.76
        bonus = min(len(steps) * 0.03, 0.15)
        return round(base + bonus, 3)