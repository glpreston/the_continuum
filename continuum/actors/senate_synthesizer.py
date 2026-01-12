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
            "Integrated multiple viewpoints, resolved tensions, and produced a "
            "balanced, coherent interpretation."
        )

    def respond(self, context, final_proposal: dict) -> str:
        return final_proposal.get("content", "")
    
    def speak_proposal(self, proposal_text: str):
        return self.speak(proposal_text)

    def reason(self, context, message: str) -> list:
        """
        Synthesizer-specific multi-step reasoning.
        Integrates perspectives and resolves tensions.
        """
        return [
            "Step 1: Identify the core intent behind the user's message.",
            "Step 2: Gather multiple perspectives relevant to the topic.",
            "Step 3: Look for common threads or shared principles.",
            "Step 4: Resolve any tensions or contradictions between perspectives.",
            "Step 5: Integrate everything into a balanced, coherent whole."
        ]

    def generate_proposal_from_steps(self, steps: list, message: str) -> str:
        """
        Synthesizer proposal: integrative, balanced, and perspective-aware.
        Combines reasoning steps into a unified, coherent response that
        directly addresses the user's message.
        """

        # 1. Actor-specific framing
        intro = (
            "Balanced in approach, as the Synthesizer, I draw together multiple "
            "perspectives to form a coherent and unified understanding."
        )

        # 2. Message interpretation
        interpretation = (
            f"Your message asks: '{message}'. I interpret this as a request "
            "to integrate viewpoints, identify common ground, and propose a "
            "harmonized direction."
        )

        # 3. Reasoning integration
        reasoning_summary = (
            "Following my reasoning steps, I begin by identifying the core "
            "perspectives involved, then compare their assumptions, highlight "
            "their points of convergence, and finally blend them into a "
            "balanced and actionable synthesis."
        )

        # 4. Actor-specific integrative output
        synthesis = (
            "Here is the integrated perspective:\n"
            "- **Perspective Mapping:** Identify the primary viewpoints and their motivations.\n"
            "- **Common Ground:** Highlight shared goals or compatible assumptions.\n"
            "- **Tensions:** Note where perspectives diverge and why.\n"
            "- **Reconciliation:** Propose ways to bridge differences.\n"
            "- **Unified Path:** Offer a balanced direction that respects all sides."
        )

        # 5. Persona-aligned closing
        closing = (
            "This synthesis reflects a harmonized and integrative reading of your request."
        )

        return f"{intro}\n\n{interpretation}\n\n{reasoning_summary}\n\n{synthesis}\n\n{closing}"
                
    def compute_confidence(self, steps: list) -> float:
        """
        Synthesizer confidence grows with integration depth.
        Slightly higher base than other actors to reflect its balancing role.
        """
        base = 0.78
        bonus = min(len(steps) * 0.035, 0.18)
        return round(base + bonus, 3)
