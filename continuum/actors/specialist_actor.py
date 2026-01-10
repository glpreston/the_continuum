# continuum/actors/specialist_actor.py

from typing import Any, Dict, Optional
from .base_actor import BaseActor

class SpecialistActor(BaseActor):
    """
    A domain-aware actor that generates more meaningful proposals
    than the BaseActor. Each specialist can implement its own
    reasoning strategy, persona tone, and confidence scoring.
    """

    def __init__(
        self,
        name: str,
        domain: str,
        persona: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, persona)
        self.domain = domain

    # ---------------------------------------------------------
    # PROPOSAL GENERATION
    # ---------------------------------------------------------
    def propose(self, context, message: str) -> Dict[str, Any]:
        """
        Generate a domain-specific proposal.
        This is intentionally simple for now, but structured so
        you can expand it into real reasoning later.
        """

        # Basic heuristic: specialists only propose if the message
        # seems relevant to their domain.
        relevance = self._estimate_relevance(message)

        if relevance < 0.2:
            # Still generate a low-confidence proposal instead of opting out completely
            proposal_text = (
                f"As a specialist in {self.domain}, I can still offer a general perspective, "
                f"even though this question is not strongly tied to my domain: "
                f"{self._generate_insight(message)}"
            )
            return {
                "actor": self.name,
                "content": proposal_text,
                    # Very low confidence, but non-zero so it passes filtering
                "confidence": 0.2,
                "metadata": {
                    "type": "low_relevance_proposal",
                    "domain": self.domain,
                    "persona": self.persona,
                },
            }

        # Otherwise, generate a simple domain-aware proposal
        proposal_text = (
            f"As a specialist in {self.domain}, I suggest considering "
            f"the following perspective: {self._generate_insight(message)}"
        )

        return {
            "actor": self.name,
            "content": proposal_text,
            "confidence": relevance,
            "metadata": {
                "type": "specialist_proposal",
                "domain": self.domain,
                "persona": self.persona,
            },
        }

    # ---------------------------------------------------------
    # FINAL RESPONSE GENERATION
    # ---------------------------------------------------------
    def respond(self, context, selected_proposal: Dict[str, Any]) -> str:
        """
        Converts the selected proposal into a final user-facing response.
        Applies persona tone if available.
        """
        content = selected_proposal.get("content", "")

        if not content:
            return ""

        # Apply persona tone if defined
        tone = self.persona.get("tone")
        if tone == "warm":
            return f"{content} I hope this perspective is helpful."
        elif tone == "direct":
            return f"{content}"
        elif tone == "analytical":
            return f"{content} This conclusion is based on logical inference."

        # Default
        return content

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------
    def _estimate_relevance(self, message: str) -> float:
        """
        Placeholder relevance estimator.
        Later, this can use embeddings, keyword matching,
        or semantic memory.
        """
        message_lower = message.lower()
        domain_lower = self.domain.lower()

        if domain_lower in message_lower:
            return 0.9

        # Simple heuristic: partial match
        if any(word in message_lower for word in domain_lower.split()):
            return 0.5

        return 0.1

    def _generate_insight(self, message: str) -> str:
        """
        Placeholder insight generator.
        Later, this can call LLMs, tools, or memory.
        """
        return f"your message relates to {self.domain}, so we can explore it from that angle."