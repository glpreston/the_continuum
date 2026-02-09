# continuum/orchestrator/jury_rubric.py
"""
Jury Rubric 3.0 — LLM‑Native, Modular, Emotion‑Aware
----------------------------------------------------

This rubric evaluates proposals using:
- Semantic relevance (embeddings)
- Structural clarity (LLM output quality)
- Emotional alignment (EI‑2.0)
- Persona alignment (LLM actor identity)
- Memory alignment
- Novelty (embedding distance)
- Integrative reasoning
- Context‑adaptive weighting

All heavy logic is delegated to micro‑modules.
"""

from typing import Dict, List, Optional, Callable, Any

# Modular scoring subsystems
from continuum.rubric.semantic import (
    score_semantic_relevance,
    score_semantic_depth,
)
from continuum.rubric.structure import score_structure
from continuum.rubric.emotion import score_emotional_alignment
from continuum.rubric.context import (
    score_memory_alignment,
    score_novelty,
    compute_contextual_weights,
    apply_persona_curve,
)


def score_integrative_reasoning(proposal: str) -> float:
    """
    Measures how well the proposal unifies multiple conceptual frameworks
    into a coherent whole.
    """
    if not proposal:
        return 0.0

    text = proposal.lower()

    # Signals of integration
    signals = [
        "integrat",
        "unify",
        "reconcile",
        "connect",
        "framework",
        "perspective",
        "tension",
        "coherent",
        "relationship",
        "interplay",
        "synthesis",
        "combined",
        "bridge",
    ]

    score = sum(1 for s in signals if s in text) / len(signals)
    return max(0.0, min(1.0, score))


# =========================================================
# MASTER SCORING FUNCTION
# =========================================================

def score_proposal(
    message: str,
    proposal: str,
    reasoning_steps: Optional[List[str]],
    llm_prompt: str,
    model_name: str,
    user_emotion: Any,
    memory_summary: str,
    all_proposals: List[str],
    actor_name: str,
    embed_fn: Optional[Callable[[str], List[float]]] = None,
) -> Dict[str, float]:
    """
    Phase‑4 scoring:
    - LLM‑aware
    - Emotion‑aware
    - Persona‑aware
    - Context‑adaptive
    """

    # -----------------------------
    # 1. Semantic scoring
    # -----------------------------
    relevance = score_semantic_relevance(message, proposal, embed_fn)
    depth = score_semantic_depth(proposal, embed_fn)

    # -----------------------------
    # 2. Structural scoring
    # -----------------------------
    structure = score_structure(proposal, llm_prompt)

    # -----------------------------
    # 3. Emotional alignment
    # -----------------------------
    emotional = score_emotional_alignment(
        user_emotion=user_emotion,
        actor_name=actor_name,
        embed_fn=embed_fn,
    )

    # -----------------------------
    # 4. Memory + Novelty
    # -----------------------------
    memory = score_memory_alignment(memory_summary, proposal, embed_fn=embed_fn)
    novelty = score_novelty(proposal, all_proposals, embed_fn=embed_fn)

    # -----------------------------
    # 5. Persona curve
    # -----------------------------
    scores: Dict[str, float] = {
        "relevance": relevance,
        "semantic_depth": depth,
        "structure": structure,
        "emotional_alignment": emotional,
        "memory_alignment": memory,
        "novelty": novelty,
        "integrative_reasoning": score_integrative_reasoning(proposal),
    }

    scores = apply_persona_curve(actor_name, scores)

    # -----------------------------
    # 6. Context‑adaptive weights
    # -----------------------------
    weights = compute_contextual_weights(message, user_emotion)

    # Defensive: only multiply over keys present in both
    total = 0.0
    for k, v in scores.items():
        w = weights.get(k, 0.0)
        total += v * w

    scores["total"] = round(total, 4)

    return scores