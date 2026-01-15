# continuum/orchestrator/jury.py

from typing import List, Dict, Any, Optional

from continuum.orchestrator.jury_rubric import score_proposal
from continuum.emotion.jury_adaptive_weights import compute_adaptive_weights


class Jury:
    """
    Jury 2.0
    --------
    Evaluates actor proposals using a structured scoring rubric.
    Selects the best proposal based on weighted criteria and provides
    a transparent explanation of the decision.
    """

    def __init__(self):
        self.embed_fn = None   # required for emotional alignment scoring

    # ---------------------------------------------------------
    # SCORE ALL PROPOSALS
    # ---------------------------------------------------------
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
                embed_fn=self.embed_fn,
            )

        return scored

    # ---------------------------------------------------------
    # SELECT WINNER
    # ---------------------------------------------------------
    def select_best(self, scored: Dict[str, Dict[str, float]]) -> Optional[str]:
        if not scored:
            return None
        return max(scored.keys(), key=lambda a: scored[a]["total"])

    # ---------------------------------------------------------
    # EXPLAIN DECISION
    # ---------------------------------------------------------
    def explain_choice(self, winner: str, scored: Dict[str, Dict[str, float]]) -> str:
        if winner not in scored:
            return "The Jury could not determine a winner."

        b = scored[winner]

        return (
            f"The Jury selected **{winner}** based on its strong performance "
            f"across multiple criteria. Key factors included:\n"
            f"- Relevance: {b['relevance']:.2f}\n"
            f"- Coherence: {b['coherence']:.2f}\n"
            f"- Reasoning Quality: {b['reasoning_quality']:.2f}\n"
            f"- Intent Alignment: {b['intent_alignment']:.2f}\n"
            f"- Emotional Alignment: {b['emotional_alignment']:.2f}\n"
            f"- Novelty: {b['novelty']:.2f}\n"
            f"- Memory Alignment: {b['memory_alignment']:.2f}\n\n"
            f"Weighted total score: **{b['total']:.3f}**."
        )

    # ---------------------------------------------------------
    # DISSENT
    # ---------------------------------------------------------
    def generate_dissent(self, winner: str, scored: Dict[str, Dict[str, float]]) -> str:
        if len(scored) < 2:
            return ""

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
        emotional_state=None,   # ⭐ NEW
    ) -> Dict[str, Any]:

        if not proposals:
            return {
                "actor": "Jury",
                "content": "No valid proposals were available.",
                "confidence": 0.0,
                "metadata": {"type": "jury_no_selection"},
            }

        # Phase 4B: Adaptive Jury Weights
        if emotional_state is not None:
            adaptive_weights = compute_adaptive_weights(emotional_state)
        else:
            adaptive_weights = {
                "relevance": 1.0,
                "coherence": 1.0,
                "reasoning_quality": 1.0,
                "intent_alignment": 1.0,
                "emotional_alignment": 1.0,
                "novelty": 1.0,
                "memory_alignment": 1.0,
            }

        # 1. Score proposals
        scored = self.score_all(
            message=message,
            proposals=proposals,
            user_emotion=user_emotion,
            memory_summary=memory_summary,
        )

        # Apply adaptive weights to totals
        for actor, dims in scored.items():
            dims["total"] = (
                dims["relevance"] * adaptive_weights["relevance"]
                + dims["coherence"] * adaptive_weights["coherence"]
                + dims["reasoning_quality"] * adaptive_weights["reasoning_quality"]
                + dims["intent_alignment"] * adaptive_weights["intent_alignment"]
                + dims["emotional_alignment"] * adaptive_weights["emotional_alignment"]
                + dims["novelty"] * adaptive_weights["novelty"]
                + dims["memory_alignment"] * adaptive_weights["memory_alignment"]
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

        winning_proposal = next(p for p in proposals if p.get("actor") == winner)

        # 3. Explanation + dissent
        explanation = self.explain_choice(winner, scored)
        dissent = self.generate_dissent(winner, scored)

        # 4. Attach metadata
        winning_proposal["metadata"]["jury_reasoning"] = explanation
        winning_proposal["metadata"]["jury_scores"] = scored[winner]
        winning_proposal["metadata"]["jury_all_scores"] = scored
        winning_proposal["metadata"]["jury_weights"] = adaptive_weights

        if dissent:
            winning_proposal["metadata"]["jury_dissent"] = dissent

        return winning_proposal