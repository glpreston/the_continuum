# continuum/orchestrator/jury.py

from typing import List, Dict, Any, Optional

class Jury:
    """
    The Jury evaluates the ranked proposals from the Senate and selects
    the best one. It may also provide reasoning or justification for
    the selection.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # SELECT THE BEST PROPOSAL
    # ---------------------------------------------------------
    def select_best(self, proposals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Select the highest-confidence proposal.
        If no proposals exist, return None.
        """
        if not proposals:
            return None

        # Proposals are already ranked by the Senate, but we sort again
        # to ensure robustness.
        sorted_proposals = sorted(
            proposals,
            key=lambda p: p.get("confidence", 0),
            reverse=True
        )

        return sorted_proposals[0]

    # ---------------------------------------------------------
    # PROVIDE REASONING
    # ---------------------------------------------------------
    def explain_choice(self, proposal: Dict[str, Any]) -> str:
        """
        Provide a simple explanation for why this proposal was chosen.
        Later, this can be expanded into chain-of-thought or structured reasoning.
        """
        actor = proposal.get("actor", "Unknown")
        confidence = proposal.get("confidence", 0)

        return (
            f"The Jury selected the proposal from {actor} "
            f"based on its confidence score of {confidence:.2f}."
        )

    # ---------------------------------------------------------
    # MAIN ENTRYPOINT
    # ---------------------------------------------------------
    def adjudicate(self, proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Full Jury pipeline:
        1. Select the best proposal
        2. Add reasoning metadata
        3. Return the final adjudicated proposal
        """
        best = self.select_best(proposals)

        if not best:
            return {
                "actor": "Jury",
                "content": "No valid proposals were available.",
                "confidence": 0.0,
                "metadata": {
                    "type": "jury_no_selection",
                },
            }

        explanation = self.explain_choice(best)

        # Attach Jury reasoning
        best["metadata"]["jury_reasoning"] = explanation

        return best