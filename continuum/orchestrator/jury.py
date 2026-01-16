# continuum/orchestrator/jury.py

from typing import List, Dict, Any, Optional

from continuum.orchestrator.jury_rubric import score_proposal
from continuum.emotion.jury_adaptive_weights import compute_adaptive_weights


class Jury:
    """
    Jury 3.0 (LLM‑aware, Rubric 3.0)
    --------------------------------
    Evaluates actor proposals using a structured scoring rubric.
    Selects the best proposal based on weighted criteria and provides
    a transparent explanation of the decision.
    """

    def __init__(self):
        # Wired in ContinuumController: used for semantic / emotional alignment
        self.embed_fn = None

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
            metadata = p.get("metadata", {})
            if "metadata" not in p:
                p["metadata"] = metadata

            # Legacy Phase‑3: hand‑crafted reasoning steps (kept for compatibility)
            reasoning = metadata.get("reasoning", [])

            # Phase‑4: LLM metadata
            llm_prompt = metadata.get("prompt_used", "")
            model_name = metadata.get("model", "")

            scored[actor] = score_proposal(
                message=message,
                proposal=content,
                reasoning_steps=reasoning,   # Phase‑3 compatibility
                llm_prompt=llm_prompt,       # Phase‑4 LLM support
                model_name=model_name,       # Phase‑4 LLM support
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
    # EXPLAIN DECISION (Rubric 3.0 fields)
    # ---------------------------------------------------------
    def explain_choice(self, winner: str, scored: Dict[str, Dict[str, float]]) -> str:
        if winner not in scored:
            return "The Jury could not determine a winner."

        b = scored[winner]

        # Use .get with defaults to avoid crashes if any field is missing
        return (
            f"The Jury selected **{winner}** based on its strong performance "
            f"across multiple criteria. Key factors included:\n"
            f"- Relevance: {b.get('relevance', 0.0):.2f}\n"
            f"- Semantic Depth: {b.get('semantic_depth', 0.0):.2f}\n"
            f"- Structure: {b.get('structure', 0.0):.2f}\n"
            f"- Emotional Alignment: {b.get('emotional_alignment', 0.0):.2f}\n"
            f"- Memory Alignment: {b.get('memory_alignment', 0.0):.2f}\n"
            f"- Novelty: {b.get('novelty', 0.0):.2f}\n\n"
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
        emotional_state=None,   # Phase 4B: adaptive weights
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
                "semantic_depth": 1.0,
                "structure": 1.0,
                "emotional_alignment": 1.0,
                "memory_alignment": 1.0,
                "novelty": 1.0,
            }

        # 1. Score proposals
        scored = self.score_all(
            message=message,
            proposals=proposals,
            user_emotion=user_emotion,
            memory_summary=memory_summary,
        )

        # Apply adaptive weights to totals (Rubric 3.0, defensive)
        for actor, dims in scored.items():
            relevance = dims.get("relevance", 0.0)
            semantic_depth = dims.get("semantic_depth", 0.0)
            structure = dims.get("structure", 0.0)
            emotional_alignment = dims.get("emotional_alignment", 0.0)
            memory_alignment = dims.get("memory_alignment", 0.0)
            novelty = dims.get("novelty", 0.0)

            dims["total"] = (
                relevance * adaptive_weights.get("relevance", 1.0)
                + semantic_depth * adaptive_weights.get("semantic_depth", 1.0)
                + structure * adaptive_weights.get("structure", 1.0)
                + emotional_alignment * adaptive_weights.get("emotional_alignment", 1.0)
                + memory_alignment * adaptive_weights.get("memory_alignment", 1.0)
                + novelty * adaptive_weights.get("novelty", 1.0)
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

        winning_proposal = next((p for p in proposals if p.get("actor") == winner), None)
        if winning_proposal is None:
            return {
                "actor": "Jury",
                "content": "The Jury could not match the winning actor to a proposal.",
                "confidence": 0.0,
                "metadata": {"type": "jury_actor_mismatch"},
            }

        # 3. Explanation + dissent
        explanation = self.explain_choice(winner, scored)
        dissent = self.generate_dissent(winner, scored)

        # 4. Attach metadata
        metadata = winning_proposal.setdefault("metadata", {})
        metadata["jury_reasoning"] = explanation
        metadata["jury_scores"] = scored[winner]
        metadata["jury_all_scores"] = scored
        # 4. Attach metadata

        # Remap legacy weight keys (Rubric 2.x → Rubric 3.0) if present
        if "coherence" in adaptive_weights or "reasoning_quality" in adaptive_weights or "intent_alignment" in adaptive_weights:
            remapped_weights = {
                "relevance": adaptive_weights.get("relevance", 1.0),
                "semantic_depth": adaptive_weights.get("reasoning_quality", 1.0),  # depth ~ reasoning_quality
                "structure": adaptive_weights.get("coherence", 1.0),               # structure ~ coherence
                "emotional_alignment": adaptive_weights.get("emotional_alignment", 1.0),
                "memory_alignment": adaptive_weights.get("memory_alignment", 1.0),
                "novelty": adaptive_weights.get("novelty", 1.0),
            }
        else:
            remapped_weights = adaptive_weights

        metadata = winning_proposal.setdefault("metadata", {})
        metadata["jury_reasoning"] = explanation
        metadata["jury_scores"] = scored[winner]
        metadata["jury_all_scores"] = scored
        metadata["jury_weights"] = remapped_weights




        if dissent:
            metadata["jury_dissent"] = dissent

        # 5. Fusion weights (Fusion 2.0)
        totals = {actor: dims["total"] for actor, dims in scored.items()}
        sum_total = sum(totals.values()) or 1.0  # avoid division by zero

        fusion_weights = {
            actor: total / sum_total
            for actor, total in totals.items()
        }

        metadata["fusion_weights"] = fusion_weights
        metadata["is_llm"] = metadata.get("type") == "llm_actor"

        return winning_proposal