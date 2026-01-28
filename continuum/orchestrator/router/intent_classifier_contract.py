# continuum/orchestrator/routing/intent_classifier_contract.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class IntentResult:
    intent: str
    confidence: float
    matched_alias: Optional[str] = None
    raw_text: Optional[str] = None


class IntentClassifierContract:
    """
    Contract for any intent classifier implementation.
    This is what the orchestrator depends on.
    """

    def classify(self, text: str) -> IntentResult:
        """
        Given raw user text, return a normalized intent result.

        Implementations may:
        - use LLMs
        - use rules
        - use embeddings
        but they MUST return IntentResult.
        """
        raise NotImplementedError