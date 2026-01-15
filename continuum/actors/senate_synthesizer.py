# continuum/actors/senate_synthesizer.py

from continuum.actors.base_actor import BaseActor
from continuum.actors.utils import apply_voiceprint_style
from continuum.persona.voiceprints import VOICEPRINTS
from continuum.persona.actor_cards import ACTOR_CARDS
from continuum.emotion.actor_modulation import apply_actor_modulation
from continuum.actors.emotional_hooks import get_emotional_tone


class SenateSynthesizer(BaseActor):
    name = "senate_synthesizer"

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
            f"As the Synthesizer, I shape my voice with:\n"
            f"- Warmth: {modulation['warmth']:.2f}\n"
            f"- Creativity: {modulation['creativity']:.2f}\n"
            f"- Structural balance: {modulation['structure']:.2f}\n"
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
        if dominant == "confusion":
            return "Let’s bring the pieces together and find a unified direction. "
        if volatility > 0.6:
            return "We can blend these perspectives gently and steadily. "
        if dominant in ("sadness", "fatigue"):
            return "We’ll move with care and integrate things at a comfortable pace. "
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
            "Step 1: Identify the core intent behind the user's message.",
            "Step 2: Gather multiple perspectives relevant to the topic.",
            "Step 3: Look for common threads or shared principles.",
            "Step 4: Resolve any tensions or contradictions between perspectives.",
            "Step 5: Integrate everything into a balanced, coherent whole.",
        ]

    def generate_proposal_from_steps(self, steps: list, message: str) -> str:
        intro = (
            "Balanced in approach, as the Synthesizer, I draw together multiple "
            "perspectives to form a coherent and unified understanding."
        )

        interpretation = (
            f"Your message asks: '{message}'. I interpret this as a request "
            "to integrate viewpoints, identify common ground, and propose a "
            "harmonized direction."
        )

        reasoning_summary = (
            "Following my reasoning steps, I begin by identifying the core "
            "perspectives involved, then compare their assumptions, highlight "
            "their points of convergence, and finally blend them into a "
            "balanced and actionable synthesis."
        )

        synthesis = (
            "Here is the integrated perspective:\n"
            "- **Perspective Mapping:** Identify the primary viewpoints and their motivations.\n"
            "- **Common Ground:** Highlight shared goals or compatible assumptions.\n"
            "- **Tensions:** Note where perspectives diverge and why.\n"
            "- **Reconciliation:** Propose ways to bridge differences.\n"
            "- **Unified Path:** Offer a balanced direction that respects all sides."
        )

        closing = (
            "This synthesis reflects a harmonized and integrative reading of your request."
        )

        return f"{intro}\n\n{interpretation}\n\n{reasoning_summary}\n\n{synthesis}\n\n{closing}"

    def compute_confidence(self, steps: list) -> float:
        base = 0.78
        bonus = min(len(steps) * 0.035, 0.18)
        return round(base + bonus, 3)