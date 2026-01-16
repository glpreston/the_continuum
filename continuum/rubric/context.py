# continuum/rubric/context.py
"""
Contextual Scoring — Jury Rubric 3.0
------------------------------------

Evaluates:
- Memory alignment (semantic)
- Novelty (embedding distance)
- Persona‑specific scoring curves
- Context‑adaptive weighting (emotion‑aware)

All scores normalized to [0, 1].
"""

from typing import Dict, List
import math


# =========================================================
# Embedding Utility
# =========================================================

def _cosine(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))
    return dot / (n1 * n2) if n1 and n2 else 0.0


# =========================================================
# Memory Alignment
# =========================================================

def score_memory_alignment(
    memory_summary: str,
    proposal: str,
    embed_fn=None,
) -> float:
    """
    Measures how well the proposal aligns with the user's memory summary.
    Uses embeddings when available.
    """

    if not memory_summary or not proposal:
        return 0.5  # neutral

    if embed_fn:
        mem_emb = embed_fn(memory_summary)
        prop_emb = embed_fn(proposal)
    else:
        return 0.5

    if mem_emb and prop_emb:
        sim = _cosine(mem_emb, prop_emb)
        return max(0.0, min(sim, 1.0))

    return 0.5


# =========================================================
# Novelty (Embedding Distance)
# =========================================================

def score_novelty(
    proposal: str,
    all_proposals: List[str],
    embed_fn=None,
) -> float:
    """
    Measures novelty as the inverse of average embedding similarity
    to other proposals.
    """

    if not proposal or not all_proposals or embed_fn is None:
        return 0.5

    prop_emb = embed_fn(proposal)
    if not prop_emb:
        return 0.5

    sims = []
    for p in all_proposals:
        if p == proposal:
            continue
        emb = embed_fn(p)
        if emb:
            sims.append(_cosine(prop_emb, emb))

    if not sims:
        return 0.5

    avg_sim = sum(sims) / len(sims)
    novelty = 1.0 - avg_sim
    return max(0.0, min(novelty, 1.0))


# =========================================================
# Persona‑Specific Scoring Curves
# =========================================================

PERSONA_CURVES = {
    "SenateAnalyst": {
        "relevance": 1.1,
        "semantic_depth": 1.1,
        "structure": 1.15,
    },
    "SenateArchitect": {
        "semantic_depth": 1.15,
        "structure": 1.1,
    },
    "SenateSynthesizer": {
        "emotional_alignment": 1.15,
        "memory_alignment": 1.1,
    },
    "SenateStoryweaver": {
        "emotional_alignment": 1.2,
        "novelty": 1.15,
    },
}


def apply_persona_curve(actor_name: str, scores: Dict[str, float]) -> Dict[str, float]:
    """
    Applies persona‑specific scoring curves to emphasize each actor's strengths.
    """

    curve = PERSONA_CURVES.get(actor_name, {})
    for k, factor in curve.items():
        if k in scores:
            scores[k] = min(scores[k] * factor, 1.0)

    return scores


# =========================================================
# Context‑Adaptive Weights
# =========================================================

BASE_WEIGHTS = {
    "relevance": 0.25,
    "semantic_depth": 0.20,
    "structure": 0.20,
    "emotional_alignment": 0.20,
    "memory_alignment": 0.10,
    "novelty": 0.05,
}


def compute_contextual_weights(
    message: str,
    emotional_state,
) -> Dict[str, float]:
    """
    Adjusts scoring weights based on emotional volatility and message tone.
    """

    weights = BASE_WEIGHTS.copy()

    # High volatility → emotional alignment matters more
    if hasattr(emotional_state, "volatility") and emotional_state.volatility > 0.4:
        weights["emotional_alignment"] += 0.05
        weights["structure"] -= 0.05

    # Calm → emphasize depth + structure
    if hasattr(emotional_state, "volatility") and emotional_state.volatility < 0.2:
        weights["semantic_depth"] += 0.05
        weights["structure"] += 0.03

    # Normalize
    total = sum(weights.values())
    for k in weights:
        weights[k] /= total

    return weights