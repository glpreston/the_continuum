# continuum/orchestrator/jury.py

from typing import List, Dict, Any, Optional

from continuum.orchestrator.jury_rubric import score_proposal


class Jury:
    """
    Jury 2.0
    --------
    Evaluates actor proposals using a structured scoring rubric.
    Selects the best proposal based on weighted criteria and provides
    a transparent explanation of the decision.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # SCORE ALL PROPOSALS
    # ---------------------------------------------------------
class Jury:
    def __init__(self):
        self.embed_fn = None   # ⭐ required

    def score_all(
        self,
        message: str,
        proposals: List[Dict[str, Any]],
        user_emotion: str = "",
        memory_summary: str = "",
    ) -> Dict[str, Dict[str, float]]:

        all_contents = [p.get("content", "") for p in proposals]
        scored = {}

        for p in proposals:
            actor = p.get("actor", "unknown")
            content = p.get("content", "")
            reasoning = p.get("metadata", {}).get("reasoning", [])

            scored[actor] = score_proposal(
                message=message,
                proposal=content,
                reasoning_steps=reasoning,
                user_emotion=user_emotion,
                memory_summary=memory_summary,
                all_proposals=all_contents,
                actor_name=actor,
                embed_fn=self.embed_fn,   # ⭐ required
            )

        return scored

    # ---------------------------------------------------------
    # SELECT WINNER BASED ON RUBRIC TOTAL
    # ---------------------------------------------------------
    def select_best(self, scored: Dict[str, Dict[str, float]]) -> Optional[str]:
        """
        Select the actor with the highest total score.
        """
        if not scored:
            return None

        return max(scored.keys(), key=lambda a: scored[a]["total"])

    # ---------------------------------------------------------
    # EXPLAIN THE DECISION
    # ---------------------------------------------------------
    def explain_choice(
        self,
        winner: str,
        scored: Dict[str, Dict[str, float]],
    ) -> str:
        """
        Generates a human-readable explanation of the Jury's decision.
        """
        if winner not in scored:
            return "The Jury could not determine a winner."

        breakdown = scored[winner]

        explanation = (
            f"The Jury selected **{winner}** based on its strong performance "
            f"across multiple criteria. Key factors included:\n"
            f"- Relevance: {breakdown['relevance']:.2f}\n"
            f"- Coherence: {breakdown['coherence']:.2f}\n"
            f"- Reasoning Quality: {breakdown['reasoning_quality']:.2f}\n"
            f"- Intent Alignment: {breakdown['intent_alignment']:.2f}\n"
            f"- Emotional Alignment: {breakdown['emotional_alignment']:.2f}\n"
            f"- Novelty: {breakdown['novelty']:.2f}\n"
            f"- Memory Alignment: {breakdown['memory_alignment']:.2f}\n\n"
            f"Weighted total score: **{breakdown['total']:.3f}**."
        )

        return explanation

    # ---------------------------------------------------------
    # OPTIONAL DISSENT
    # ---------------------------------------------------------
    def generate_dissent(
        self,
        winner: str,
        scored: Dict[str, Dict[str, float]],
    ) -> str:
        """
        Identifies the runner-up and explains why it was close.
        """
        if len(scored) < 2:
            return ""

        # Sort actors by total score
        sorted_actors = sorted(
            scored.items(),
            key=lambda item: item[1]["total"],
            reverse=True,
        )

        runner_up, runner_scores = sorted_actors[1]

        if runner_up == winner:
            return ""

        gap = scored[winner]["total"] - runner_scores["total"]

        return (
            f"Dissenting Note: {runner_up} offered a strong alternative with a "
            f"total score of {runner_scores['total']:.3f}, trailing the winner "
            f"by {gap:.3f}. The Jury acknowledges its strengths but found the "
            f"winner's proposal more aligned overall."
        )

    # ---------------------------------------------------------
    # MAIN ENTRYPOINT
    # ---------------------------------------------------------
    def adjudicate(
        self,
        proposals: List[Dict[str, Any]],
        message: str = "",
        user_emotion: str = "",
        memory_summary: str = "",
    ) -> Dict[str, Any]:
        """
        Full Jury 2.0 pipeline:
        1. Score all proposals
        2. Select winner
        3. Generate explanation + dissent
        4. Attach metadata to winning proposal
        """
        if not proposals:
            return {
                "actor": "Jury",
                "content": "No valid proposals were available.",
                "confidence": 0.0,
                "metadata": {"type": "jury_no_selection"},
            }

        # 1. Score proposals
        scored = self.score_all(
            message=message,
            proposals=proposals,
            user_emotion=user_emotion,
            memory_summary=memory_summary,
        )

        # 2. Select winner
        winner = self.select_best(scored)
        if not winner:
            return {
                "actor": "Jury",
                "content": "The Jury could not determine a winner.",
                "confidence": 0.0,
                "metadata": {"type": "jury_no_selection"},
            }

        # Find the winning proposal
        winning_proposal = next(
            p for p in proposals if p.get("actor") == winner
        )

        # 3. Explanation + dissent
        explanation = self.explain_choice(winner, scored)
        dissent = self.generate_dissent(winner, scored)

        # 4. Attach metadata
        winning_proposal["metadata"]["jury_reasoning"] = explanation
        winning_proposal["metadata"]["jury_scores"] = scored[winner]
        winning_proposal["metadata"]["jury_all_scores"] = scored
        if dissent:
            winning_proposal["metadata"]["jury_dissent"] = dissent

        return winning_proposal