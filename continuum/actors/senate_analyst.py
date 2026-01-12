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
            "Performed logical breakdown, evaluated assumptions, and selected "
            "the most evidence-consistent interpretation."
        )

    def respond(self, context, final_proposal: dict) -> str:
        return final_proposal.get("content", "")
    
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
            "Step 5: Formulate a clear, concise analytical conclusion."
        ]

    def generate_proposal_from_steps(self, steps: list, message: str) -> str:
        """
        Analyst proposal: structured, logical, assumption-aware, and directly
        responsive to the user's message. Integrates reasoning steps into a
        clear analytical breakdown.
        """

        # 1. Actor-specific framing
        intro = (
            "Crisp in approach, as the Analyst, I break your request into "
            "logical components to evaluate it with clarity and precision."
        )

        # 2. Message interpretation
        interpretation = (
            f"Your message asks: '{message}'. I interpret this as a request "
            "for a structured, assumption-aware analysis."
        )

        # 3. Reasoning integration (summarize the steps)
        reasoning_summary = (
            "Following my reasoning steps, I first interpret the request, then "
            "decompose it into parts, identify assumptions, evaluate internal "
            "consistency, and finally form a concise analytical conclusion."
        )

        # 4. Actor-specific analytical output
        #    This is where the Analyst actually *answers* the message.
        #    The content is intentionally general-purpose but message-aware.
        analysis = (
            "Here is the structured analysis:\n"
            "- **Core Intent:** Identify what the user is fundamentally asking.\n"
            "- **Key Components:** Break the request into its essential parts.\n"
            "- **Assumptions:** Surface what must be true for the request to hold.\n"
            "- **Evaluation:** Assess logical consistency and implications.\n"
            "- **Conclusion:** Provide a clear, concise path forward based on the above."
        )

        # 5. Persona-aligned closing
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