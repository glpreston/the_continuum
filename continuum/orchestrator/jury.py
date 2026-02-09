# continuum/orchestrator/jury.py
from typing import List, Dict, Any, Optional

from continuum.orchestrator.jury_rubric import score_proposal
from continuum.emotion.jury_adaptive_weights import compute_adaptive_weights


# ============================================================
# JURY CONSTANTS (Phase‑5)
# ============================================================

# Intent‑aware actor weighting (Greeter excluded from non‑greeting)
INTENT_ACTOR_WEIGHTS = {
    "greeting": {"Greeter": 1.0},
    "chitchat": {"Greeter": 1.0},

    "big_idea": {
        "Architect": 1.0,
        "Analyst": 1.0,
        "Storyweaver": 0.7,
    },

    "analysis": {
        "Analyst": 1.0,
        "Architect": 0.8,
    },

    "story": {
        "Storyweaver": 1.0,
    },

    "summary": {
        "Synthesizer": 1.0,
    },
}

# Default fallback if intent not recognized
DEFAULT_INTENT_WEIGHTS = {
    "Architect": 1.0,
    "Analyst": 1.0,
    "Storyweaver": 0.8,
    "Synthesizer": 0.8,
    "Greeter": 0.0,  # Greeter excluded by default
}


class Jury:
    """
    Jury 5.0 (Phase‑5)
    -------------------
    - Intent‑aware actor scoring
    - Strict proposal validation
    - Adaptive emotional weighting
    - Rubric 3.0 scoring
    - Fusion‑ready output
    """

    def __init__(self):
        self.embed_fn = None  # wired by controller

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
        scored: Dict[str, Dict[str, float]] = {}

        for p in proposals:
            actor = p.get("actor", "unknown")
            content = p.get("content", "")

            # Ensure metadata exists
            metadata = p.setdefault("metadata", {})

            # Legacy compatibility fields
            reasoning = metadata.get("reasoning", [])
            llm_prompt = metadata.get("prompt_used", "")
            model_name = metadata.get("model", "")

            # Score using Rubric 3.0
            scored[actor] = score_proposal(
                message=message,
                proposal=content,
                reasoning_steps=reasoning,
                llm_prompt=llm_prompt,
                model_name=model_name,
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
            f"The Jury selected **{winner}** based on its strong performance across "
            f"multiple criteria:\n"
            f"- Relevance: {b.get('relevance', 0.0):.2f}\n"
            f"- Semantic Depth: {b.get('semantic_depth', 0.0):.2f}\n"
            f"- Structure: {b.get('structure', 0.0):.2f}\n"
            f"- Emotional Alignment: {b.get('emotional_alignment', 0.0):.2f}\n"
            f"- Memory Alignment: {b.get('memory_alignment', 0.0):.2f}\n"
            f"- Novelty: {b.get('novelty', 0.0):.2f}\n"
            f"- Integrative Reasoning: {b.get('integrative_reasoning', 0.0):.2f}\n\n"
            f"Weighted total score: **{b.get('total', 0.0):.3f}**."
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
            f"by {gap:.3f}."
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
        emotional_state=None,
        intent: str = None,  # NEW: intent-aware scoring
    ) -> Dict[str, Any]:

        # No proposals at all
        if not proposals:
            return {
                "actor": "Jury",
                "content": "No valid proposals were available.",
                "confidence": 0.0,
                "metadata": {"type": "jury_no_selection"},
            }

        # -----------------------------------------------------
        # Intent‑aware actor weighting
        # -----------------------------------------------------
        intent_weights = INTENT_ACTOR_WEIGHTS.get(intent, DEFAULT_INTENT_WEIGHTS)

        # -----------------------------------------------------
        # Strict proposal validation
        # -----------------------------------------------------
        valid_proposals = []
        for p in proposals:
            actor = p.get("actor")
            content = p.get("content")

            # Exclude Greeter from non‑greeting intents
            if actor == "Greeter" and intent not in ("greeting", "chitchat"):
                continue

            # Exclude empty/error proposals
            if not content:
                continue

            valid_proposals.append(p)

        if not valid_proposals:
            return {
                "actor": "Jury",
                "content": "All proposals were invalid for this intent.",
                "confidence": 0.0,
                "metadata": {"type": "jury_no_valid_proposals"},
            }

        # -----------------------------------------------------
        # Adaptive emotional weights
        # -----------------------------------------------------
        if emotional_state is not None:
            adaptive_weights = compute_adaptive_weights(emotional_state)
        else:
            adaptive_weights = {
                "relevance": 1.0,
                "semantic_depth": 1.8,
                "structure": 1.3,
                "emotional_alignment": 0.8,
                "memory_alignment": 0.7,
                "novelty": 0.6,
                "integrative_reasoning": 1.2,
            }

        # Normalize adaptive weights
        norm = sum(adaptive_weights.values()) or 1.0
        normalized_weights = {k: v / norm for k, v in adaptive_weights.items()}

        # -----------------------------------------------------
        # Score proposals
        # -----------------------------------------------------
        scored = self.score_all(
            message=message,
            proposals=valid_proposals,
            user_emotion=user_emotion,
            memory_summary=memory_summary,
        )

        # -----------------------------------------------------
        # Apply intent‑actor weights + adaptive weights
        # -----------------------------------------------------
        for actor, dims in scored.items():
            actor_weight = intent_weights.get(actor, 0.0)

            dims["total"] = actor_weight * sum(
                dims.get(k, 0.0) * normalized_weights.get(k, 0.0)
                for k in normalized_weights
            )

        # -----------------------------------------------------
        # Select winner
        # -----------------------------------------------------
        winner = self.select_best(scored)
        if not winner:
            return {
                "actor": "Jury",
                "content": "The Jury could not determine a winner.",
                "confidence": 0.0,
                "metadata": {"type": "jury_no_selection"},
            }

        winning_proposal = next(
            (p for p in valid_proposals if p.get("actor") == winner), None
        )

        if winning_proposal is None:
            return {
                "actor": "Jury",
                "content": "The Jury could not match the winning actor to a proposal.",
                "confidence": 0.0,
                "metadata": {"type": "jury_actor_mismatch"},
            }

        # -----------------------------------------------------
        # Explanation + dissent
        # -----------------------------------------------------
        explanation = self.explain_choice(winner, scored)
        dissent = self.generate_dissent(winner, scored)

        # -----------------------------------------------------
        # Attach metadata
        # -----------------------------------------------------
        metadata = winning_proposal.setdefault("metadata", {})
        metadata["jury_reasoning"] = explanation
        metadata["jury_scores"] = scored[winner]
        metadata["jury_all_scores"] = scored
        metadata["jury_weights"] = intent_weights

        if dissent:
            metadata["jury_dissent"] = dissent

        # -----------------------------------------------------
        # Fusion weights
        # -----------------------------------------------------
        totals = {actor: dims["total"] for actor, dims in scored.items()}
        sum_total = sum(totals.values()) or 1.0

        fusion_weights = {
            actor: total / sum_total
            for actor, total in totals.items()
        }

        metadata["fusion_weights"] = fusion_weights

        return winning_proposal