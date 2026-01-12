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

    # ---------------------------------------------------------
    # AUDIO: speak proposal in Architect's own voice
    # ---------------------------------------------------------
    def speak_proposal(self, proposal_text: str):
        return self.speak(proposal_text)

    # ---------------------------------------------------------
    # PHASE 3: MULTI-STEP REASONING
    # ---------------------------------------------------------
    def reason(self, context, message: str) -> list:
        """
        Architect-specific multi-step reasoning.
        Focuses on structure, systems, and dependencies.
        """
        return [
            "Step 1: Identify the structural nature of the user's request.",
            "Step 2: Break the problem into its core components.",
            "Step 3: Map relationships and dependencies between components.",
            "Step 4: Identify constraints, requirements, and boundary conditions.",
            "Step 5: Formulate a clear, ordered blueprint for addressing the request.",
        ]

    def generate_proposal_from_steps(self, steps: list, message: str) -> str:
        """
        Architect proposal: structural, modular, and systems-oriented.
        Integrates reasoning steps into a blueprint-style response that
        directly addresses the user's message.
        """

        # 1. Actor-specific framing
        intro = (
            "Structured in approach, as the Architect, I interpret your request "
            "through systems, components, and the relationships that bind them."
        )

        # 2. Message interpretation
        interpretation = (
            f"Your message asks: '{message}'. I interpret this as a need for a "
            "clear structural breakdown that identifies modules, interfaces, "
            "and the flow of responsibility."
        )

        # 3. Reasoning integration
        reasoning_summary = (
            "Following my reasoning steps, I begin by identifying the core "
            "system intent, then outline the major components, define their "
            "interactions, consider constraints, and finally assemble these "
            "into a coherent architectural pattern."
        )

        # 4. Actor-specific architectural output
        architecture = (
            "Here is the architectural blueprint:\n"
            "- **Core Objective:** Establish the primary purpose and constraints.\n"
            "- **Major Components:** Identify the modules or subsystems required.\n"
            "- **Interfaces:** Define how components communicate and exchange data.\n"
            "- **Data Flow:** Map the movement of information through the system.\n"
            "- **Constraints:** Note performance, scalability, or reliability factors.\n"
            "- **Integration Pattern:** Assemble the above into a unified architecture."
        )

        # 5. Persona-aligned closing
        closing = (
            "This blueprint reflects a modular and coherent structure aligned "
            "with your request."
        )

        return f"{intro}\n\n{interpretation}\n\n{reasoning_summary}\n\n{architecture}\n\n{closing}"
        
    def compute_confidence(self, steps: list) -> float:
        """
        Architect confidence grows with structural clarity.
        Slightly lower base than Analyst, but strong when the problem is well-defined.
        """
        base = 0.80
        bonus = min(len(steps) * 0.03, 0.15)
        return round(base + bonus, 3)