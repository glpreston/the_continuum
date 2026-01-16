# continuum/rubric/semantic.py
"""
Semantic Scoring — Jury Rubric 3.0
----------------------------------

Provides:
- Semantic relevance (message ↔ proposal)
- Semantic depth (proposal ↔ depth prototype)
- Embedding utilities with safe fallbacks

All functions return values in [0, 1].
"""

from typing import List, Optional
import math

from continuum.memory.semantic import embed as get_embedding


# =========================================================
# Embedding Utilities
# =========================================================

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))
    return dot / (n1 * n2) if n1 and n2 else 0.0


# =========================================================
# Semantic Relevance
# =========================================================

def score_semantic_relevance(
    message: str,
    proposal: str,
    embed_fn=None,
) -> float:
    """
    Measures how semantically aligned the proposal is with the user's message.
    Uses embeddings when available; falls back to 0.0 if insufficient data.
    """

    if not message or not proposal:
        return 0.0

    # Prefer injected embed_fn (from controller)
    if embed_fn:
        msg_emb = embed_fn(message)
        prop_emb = embed_fn(proposal)
    else:
        msg_emb = get_embedding(message)
        prop_emb = get_embedding(proposal)

    if msg_emb and prop_emb:
        sim = cosine_similarity(msg_emb, prop_emb)
        return max(0.0, min(sim, 1.0))

    return 0.0


# =========================================================
# Semantic Depth
# =========================================================

DEPTH_PROTOTYPE = (
    "deep insight, abstraction, conceptual reasoning, multi-step logic, "
    "non-obvious connections, synthesis, evaluation, meta-cognition"
)

def score_semantic_depth(
    proposal: str,
    embed_fn=None,
) -> float:
    """
    Measures how conceptually deep the proposal is.
    Uses embedding similarity to a depth prototype.
    """

    if not proposal:
        return 0.0

    if embed_fn:
        prop_emb = embed_fn(proposal)
        depth_emb = embed_fn(DEPTH_PROTOTYPE)
    else:
        prop_emb = get_embedding(proposal)
        depth_emb = get_embedding(DEPTH_PROTOTYPE)

    if prop_emb and depth_emb:
        sim = cosine_similarity(prop_emb, depth_emb)
        return max(0.0, min(sim, 1.0))

    return 0.0