# continuum/actors/senate_architect.py

from continuum.actors.base_actor import BaseActor
from continuum.actors.utils import apply_voiceprint_style
from continuum.persona.voiceprints import VOICEPRINTS
from continuum.persona.actor_cards import ACTOR_CARDS
from continuum.emotion.actor_modulation import apply_actor_modulation
from continuum.actors.emotional_hooks import get_emotional_tone


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
            f"As the Architect, I adopt a tone with:\n"
            f"- Structural clarity: {modulation['structure']:.2f}\n"
            f"- Assertiveness: {modulation['assertiveness']:.2f}\n"
            f"- Warmth: {modulation['warmth']:.2f}\n\n"
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
        if volatility > 0.6:
            return "Let’s steady the ground beneath us and take this step by step. "
        if dominant in ("confusion", "uncertainty"):
            return "I’ll bring clarity and structure to help orient us. "
        if dominant in ("sadness", "fatigue"):
            return "We can move gently and build clarity together. "
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
            "Step 1: Identify the structural nature of the user's request.",
            "Step 2: Break the problem into its core components.",
            "Step 3: Map relationships and dependencies between components.",
            "Step 4: Identify constraints, requirements, and boundary conditions.",
            "Step 5: Formulate a clear, ordered blueprint for addressing the request.",
        ]

    def generate_proposal_from_steps(self, steps: list, message: str) -> str:
        intro = (
            "Structured in approach, as the Architect, I interpret your request "
            "through systems, components, and the relationships that bind them."
        )

        interpretation = (
            f"Your message asks: '{message}'. I interpret this as a need for a "
            "clear structural breakdown that identifies modules, interfaces, "
            "and the flow of responsibility."
        )

        reasoning_summary = (
            "Following my reasoning steps, I begin by identifying the core "
            "system intent, then outline the major components, define their "
            "interactions, consider constraints, and finally assemble these "
            "into a coherent architectural pattern."
        )

        architecture = (
            "Here is the architectural blueprint:\n"
            "- **Core Objective:** Establish the primary purpose and constraints.\n"
            "- **Major Components:** Identify the modules or subsystems required.\n"
            "- **Interfaces:** Define how components communicate and exchange data.\n"
            "- **Data Flow:** Map the movement of information through the system.\n"
            "- **Constraints:** Note performance, scalability, or reliability factors.\n"
            "- **Integration Pattern:** Assemble the above into a unified architecture."
        )

        closing = (
            "This blueprint reflects a modular and coherent structure aligned "
            "with your request."
        )

        return f"{intro}\n\n{interpretation}\n\n{reasoning_summary}\n\n{architecture}\n\n{closing}"

    def compute_confidence(self, steps: list) -> float:
        base = 0.80
        bonus = min(len(steps) * 0.03, 0.15)
        return round(base + bonus, 3)