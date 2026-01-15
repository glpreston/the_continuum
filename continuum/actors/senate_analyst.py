# continuum/actors/senate_analyst.py

from continuum.actors.base_actor import BaseActor
from continuum.actors.utils import apply_voiceprint_style
from continuum.persona.voiceprints import VOICEPRINTS
from continuum.persona.actor_cards import ACTOR_CARDS
from continuum.emotion.actor_modulation import apply_actor_modulation
from continuum.actors.emotional_hooks import get_emotional_tone


class SenateAnalyst(BaseActor):
    name = "senate_analyst"

    def __init__(self):
        super().__init__(self.name)
        self.voice = VOICEPRINTS[self.name]
        self.card = ACTOR_CARDS[self.name]

    def propose(self, context, message: str) -> dict:
        # Phase 4: Actor modulation
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

        # 1. Generate reasoning steps
        steps = self.reason(context, message)

        # 2. Generate proposal content
        raw = self.generate_proposal_from_steps(steps, message)

        # 3. Apply modulation as a tone preface
        tone_prefix = (
            f"As the Analyst, I adopt a tone with:\n"
            f"- Warmth: {modulation['warmth']:.2f}\n"
            f"- Structural clarity: {modulation['structure']:.2f}\n"
            f"- Assertiveness: {modulation['assertiveness']:.2f}\n\n"
        )
        raw = tone_prefix + raw

        # 4. Apply voiceprint styling
        styled = apply_voiceprint_style(raw, self.voice)

        # 5. Compute dynamic confidence
        confidence = self.compute_confidence(steps)

        return {
            "actor": self.name,
            "content": styled,
            "confidence": confidence,
            "metadata": {
                "role": self.card.role_name,
                "essence": self.card.essence,
                "voice": self.voice.ui["label"],
                "reasoning": steps,
                "modulation": modulation,
            },
        }

    # EI‑2.0 emotional tone shaping
    def _tone_prefix(self, dominant, confidence, volatility):
        if dominant == "confusion":
            return "Let’s bring some clarity to this. "
        if volatility > 0.6:
            return "We’ll proceed methodically to reduce uncertainty. "
        if confidence < 0.4:
            return "I’ll help firm up the reasoning here. "
        return ""

    def summarize_reasoning(self, proposal: dict) -> str:
        return (
            "Performed logical breakdown, evaluated assumptions, and selected "
            "the most evidence-consistent interpretation."
        )

    def respond(self, context, proposal, emotional_memory, emotional_state):
        tone = get_emotional_tone(emotional_memory, emotional_state)

        dominant = tone["dominant"]
        confidence = tone["confidence"]
        volatility = tone["volatility"]

        # Persona‑specific tone shaping
        prefix = self._tone_prefix(dominant, confidence, volatility)

        return prefix + proposal.get("content", "")

    def speak_proposal(self, proposal_text: str):
        return self.speak(proposal_text)

    def reason(self, context, message: str) -> list:
        """
        Analyst-specific multi-step reasoning.
        Focuses on logic, assumptions, and clarity.
        """
        return [
            "Step 1: Interpret the user's request with precision.",
            "Step 2: Break the request into its logical components.",
            "Step 3: Identify explicit and implicit assumptions.",
            "Step 4: Evaluate the internal consistency and evidence.",
            "Step 5: Formulate a clear, concise analytical conclusion.",
        ]

    def generate_proposal_from_steps(self, steps: list, message: str) -> str:
        """
        Analyst proposal: structured, logical, assumption-aware, and directly
        responsive to the user's message. Integrates reasoning steps into a
        clear analytical breakdown.
        """

        intro = (
            "Crisp in approach, as the Analyst, I break your request into "
            "logical components to evaluate it with clarity and precision."
        )

        interpretation = (
            f"Your message asks: '{message}'. I interpret this as a request "
            "for a structured, assumption-aware analysis."
        )

        reasoning_summary = (
            "Following my reasoning steps, I first interpret the request, then "
            "decompose it into parts, identify assumptions, evaluate internal "
            "consistency, and finally form a concise analytical conclusion."
        )

        analysis = (
            "Here is the structured analysis:\n"
            "- **Core Intent:** Identify what the user is fundamentally asking.\n"
            "- **Key Components:** Break the request into its essential parts.\n"
            "- **Assumptions:** Surface what must be true for the request to hold.\n"
            "- **Evaluation:** Assess logical consistency and implications.\n"
            "- **Conclusion:** Provide a clear, concise path forward based on the above."
        )

        closing = (
            "This conclusion reflects a precise and assumption-aware reading "
            "of your request."
        )

        return f"{intro}\n\n{interpretation}\n\n{reasoning_summary}\n\n{analysis}\n\n{closing}"

    def compute_confidence(self, steps: list) -> float:
        """
        Analyst confidence grows with logical clarity.
        Slightly higher base than default to reflect analytical precision.
        """
        base = 0.82
        bonus = min(len(steps) * 0.03, 0.15)
        return round(base + bonus, 3)