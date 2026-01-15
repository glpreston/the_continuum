# continuum/orchestrator/jury_rubric.py

import os
from continuum.memory.semantic import embed as get_embedding

"""
Jury 2.2 Scoring Rubric (Semantic-Ready)
---------------------------------------
Upgraded scoring criteria, weights, and evaluation functions for Phase 3.

- Semantic relevance via embeddings (when available)
- Semantic intent alignment via embeddings + actor domains
- Heuristic fallbacks when embeddings are not wired yet

Each criterion returns a score between 0.0 and 1.0.
The Jury aggregates these using weighted scoring.
"""

from typing import Dict, List
import math
import difflib

# ---------------------------------------------------------
# WEIGHTS (tunable)
# ---------------------------------------------------------
RUBRIC_WEIGHTS = {
    "relevance": 0.25,
    "coherence": 0.20,
    "reasoning_quality": 0.20,
    "intent_alignment": 0.15,
    "emotional_alignment": 0.10,
    "novelty": 0.05,
    "memory_alignment": 0.05,
}

# ---------------------------------------------------------
# ACTOR DOMAINS
# ---------------------------------------------------------
ACTOR_DOMAINS = {
    "senate_analyst": "technical",
    "senate_architect": "structural",
    "senate_synthesizer": "integrative",
    "senate_storyweaver": "creative",
}

# ---------------------------------------------------------
# Emotional Profiles
# ---------------------------------------------------------
ACTOR_EMOTIONAL_PROFILES = {
    "senate_analyst": "neutral, objective, detached, logical",
    "senate_architect": "calm, structured, methodical, steady",
    "senate_synthesizer": "balanced, empathetic, integrative, warm",
    "senate_storyweaver": "emotional, expressive, imaginative, heartfelt"
}

# ---------------------------------------------------------
# BASIC TEXT UTILITIES
# ---------------------------------------------------------
STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
    "by", "at", "from", "as", "is", "are", "was", "were", "be", "being",
    "been", "this", "that", "it", "its", "your", "you", "i", "we", "they",
    "their", "our", "us", "about", "into", "over", "under", "between",
}

def tokenize(text: str) -> List[str]:
    return [
        t.strip(".,!?;:()[]{}'\"").lower()
        for t in text.split()
        if t.strip(".,!?;:()[]{}'\"")
    ]

def content_words(text: str) -> List[str]:
    return [w for w in tokenize(text) if w not in STOPWORDS]

def jaccard_similarity(a: List[str], b: List[str]) -> float:
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    inter = len(sa & sb)
    union = len(sa | sb)
    if union == 0:
        return 0.0
    return inter / union

def sequence_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

# ---------------------------------------------------------
# EMBEDDING HOOKS (wire these to your model)
# ---------------------------------------------------------

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)

# ---------------------------------------------------------
# INTENT / DOMAIN PROTOTYPES (for semantic intent)
# ---------------------------------------------------------
DOMAIN_PROTOTYPES = {
    "technical": "Explain, analyze, compare tradeoffs, performance, complexity, synchronous, asynchronous, processing, evaluation.",
    "creative": "Write a story, vignette, poem, emotional scene, metaphor, imagery, character, lighthouse, forgotten memory.",
    "structural": "Design a modular architecture, framework, components, interfaces, data flow, constraints, scalability, reliability.",
    "integrative": "Summarize perspectives, reconcile views, propose a balanced path forward, synthesize, unify, bridge differences.",
}

def get_domain_embedding(domain: str) -> List[float]:
    text = DOMAIN_PROTOTYPES.get(domain, "")
    if not text:
        return []
    return get_embedding(text)

# ---------------------------------------------------------
# SCORING FUNCTIONS
# ---------------------------------------------------------
def score_relevance(message: str, proposal: str) -> float:
    """
    Semantic relevance:
    - If embeddings available: cosine(message_emb, proposal_emb)
    - Else: fallback to token + sequence similarity
    """
    
    if not message or not proposal:
        #print("→ SHORT-CIRCUIT: empty message or proposal")
        return 0.0


    msg_emb = get_embedding(message)
    prop_emb = get_embedding(proposal)
    
    if msg_emb and prop_emb:
        score = cosine_similarity(msg_emb, prop_emb)
        return max(0.0, min(score, 1.0))

    # Heuristic fallback
    msg_words = content_words(message)
    prop_words = content_words(proposal)
    jacc = jaccard_similarity(msg_words, prop_words)
    seq = sequence_similarity(message, proposal)
    score = 0.6 * jacc + 0.4 * seq
    return max(0.0, min(score, 1.0))

def score_coherence(proposal: str) -> float:
    """
    Measures structural clarity and logical flow.
    """
    if not proposal:
        return 0.0

    score = 0.0
    sentences = [s for s in proposal.split(".") if s.strip()]
    if len(sentences) >= 2:
        score += 0.4
    if "\n\n" in proposal:
        score += 0.2
    if "," in proposal:
        score += 0.2
    if len(proposal.split()) > 40:
        score += 0.2

    return min(score, 1.0)

def score_reasoning_quality(steps: List[str]) -> float:
    """
    Measures depth and clarity of reasoning.
    """
    if not steps:
        return 0.0

    base = min(len(steps) * 0.15, 0.75)
    structure_bonus = 0.0

    for s in steps:
        s_lower = s.lower()
        if "step" in s_lower:
            structure_bonus += 0.03
        if any(v in s_lower for v in ["identify", "evaluate", "map", "formulate", "summarize", "synthesize"]):
            structure_bonus += 0.02

    structure_bonus = min(structure_bonus, 0.25)
    return max(0.0, min(base + structure_bonus, 1.0))

def score_intent_alignment(message: str, proposal: str, actor_name: str) -> float:
    """
    Semantic intent alignment:

    - Embed the message
    - Compare it to each domain prototype
    - Get a soft distribution over domains
    - Compare actor's home domain to message domain
    - Optionally blend in proposal-domain similarity
    """
    if not message or not proposal:
        return 0.0

    msg_emb = get_embedding(message)
    if not msg_emb:
        # If no embeddings, fall back to neutral
        return 0.0

    # Compute similarity of message to each domain prototype
    domain_scores = {}
    for domain, proto_text in DOMAIN_PROTOTYPES.items():
        proto_emb = get_domain_embedding(domain)
        if not proto_emb:
            domain_scores[domain] = 0.0
        else:
            domain_scores[domain] = cosine_similarity(msg_emb, proto_emb)

    # Normalize to a distribution
    total = sum(max(v, 0.0) for v in domain_scores.values())
    if total == 0:
        msg_dist = {k: 0.25 for k in DOMAIN_PROTOTYPES.keys()}
    else:
        msg_dist = {k: max(v, 0.0) / total for k, v in domain_scores.items()}

    # Actor domain as one-hot
    actor_domain = ACTOR_DOMAINS.get(actor_name, "")
    actor_dist = {k: 0.0 for k in DOMAIN_PROTOTYPES.keys()}
    if actor_domain in actor_dist:
        actor_dist[actor_domain] = 1.0

    # Proposal domain: which prototype is it closest to?
    prop_emb = get_embedding(proposal)
    if prop_emb:
        prop_scores = {}
        for domain, proto_text in DOMAIN_PROTOTYPES.items():
            proto_emb = get_domain_embedding(domain)
            if not proto_emb:
                prop_scores[domain] = 0.0
            else:
                prop_scores[domain] = cosine_similarity(prop_emb, proto_emb)
        total_prop = sum(max(v, 0.0) for v in prop_scores.values())
        if total_prop == 0:
            prop_dist = {k: 0.25 for k in DOMAIN_PROTOTYPES.keys()}
        else:
            prop_dist = {k: max(v, 0.0) / total_prop for k, v in prop_scores.items()}
    else:
        prop_dist = {k: 0.25 for k in DOMAIN_PROTOTYPES.keys()}

    # Cosine-like similarity over distributions
    def dist_sim(a: Dict[str, float], b: Dict[str, float]) -> float:
        keys = set(a.keys()) | set(b.keys())
        va = [a.get(k, 0.0) for k in keys]
        vb = [b.get(k, 0.0) for k in keys]
        dot = sum(x * y for x, y in zip(va, vb))
        na = math.sqrt(sum(x * x for x in va))
        nb = math.sqrt(sum(y * y for y in vb))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    msg_actor = dist_sim(msg_dist, actor_dist)
    msg_prop = dist_sim(msg_dist, prop_dist)

    # Actor domain matters most, proposal domain refines
    score = 0.7 * msg_actor + 0.3 * msg_prop
    return max(0.0, min(score, 1.0))

def score_emotional_alignment(user_emotion, actor_name: str, embed_fn) -> float:
    """
    EI‑2.0 aware emotional alignment.

    Supports:
    - EI‑2.0 dict:
        {
            "smoothed_state": {...},
            "dominant_emotion": str | None,
            "confidence": float,
            "volatility": float,
        }
    - Legacy string user_emotion (falls back to semantic profile match)
    """

    # -----------------------------
    # Backwards‑compatible fallback
    # -----------------------------
    if isinstance(user_emotion, str):
        # Old behavior: treat as a simple label / description
        if not user_emotion:
            return 0.5

        actor_profile = ACTOR_EMOTIONAL_PROFILES.get(actor_name, "")
        if not actor_profile or embed_fn is None:
            return 0.5

        user_vec = embed_fn(user_emotion)
        actor_vec = embed_fn(actor_profile)

        dot = sum(u * a for u, a in zip(user_vec, actor_vec))
        norm_u = sum(u * u for u in user_vec) ** 0.5
        norm_a = sum(a * a for a in actor_vec) ** 0.5

        if norm_u == 0 or norm_a == 0:
            return 0.5

        similarity = dot / (norm_u * norm_a)
        return (similarity + 1) / 2  # [-1,1] → [0,1]

    # -----------------------------
    # EI‑2.0 structured emotion
    # -----------------------------
    if not isinstance(user_emotion, dict):
        return 0.5

    smoothed = user_emotion.get("smoothed_state", {}) or {}
    dominant = user_emotion.get("dominant_emotion", None)
    confidence = float(user_emotion.get("confidence", 0.0) or 0.0)
    volatility = float(user_emotion.get("volatility", 0.0) or 0.0)

    actor_profile = ACTOR_EMOTIONAL_PROFILES.get(actor_name, "")
    if not actor_profile or embed_fn is None:
        return 0.5

    # Build a textual fingerprint of the emotional state for embedding
    # e.g. "dominant: sadness; calm: 0.2; anxiety: 0.7; ..."
    parts = []
    if dominant:
        parts.append(f"dominant: {dominant}")
    for dim, val in smoothed.items():
        parts.append(f"{dim}: {val:.3f}")
    emo_text = "; ".join(parts) if parts else "neutral"

    user_vec = embed_fn(emo_text)
    actor_vec = embed_fn(actor_profile)

    dot = sum(u * a for u, a in zip(user_vec, actor_vec))
    norm_u = sum(u * u for u in user_vec) ** 0.5
    norm_a = sum(a * a for a in actor_vec) ** 0.5

    if norm_u == 0 or norm_a == 0:
        base = 0.5
    else:
        similarity = dot / (norm_u * norm_a)
        base = (similarity + 1) / 2  # [-1,1] → [0,1]

    # Confidence boosts alignment; volatility dampens it
    volatility_factor = 1.0 / (1.0 + volatility)      # more volatility → smaller factor
    confidence_factor = 0.5 + 0.5 * confidence        # [0.5, 1.0]

    score = base * volatility_factor * confidence_factor

    # Clamp to [0,1]
    return max(0.0, min(score, 1.0))

def score_novelty(proposal: str, all_proposals: List[str]) -> float:
    """
    Measures uniqueness relative to other actors.
    """
    if not proposal or not all_proposals:
        return 0.0

    sims = []
    for p in all_proposals:
        if p is proposal:
            continue
        sims.append(sequence_similarity(proposal, p))

    if not sims:
        return 0.5

    avg_sim = sum(sims) / len(sims)
    novelty = 1.0 - avg_sim
    return max(0.0, min(novelty, 1.0))

def score_memory_alignment(memory_summary: str, proposal: str) -> float:
    """
    Measures whether the proposal respects long-term context.
    """
    if not memory_summary or not proposal:
        return 0.5

    mem_words = content_words(memory_summary)
    prop_words = content_words(proposal)
    jacc = jaccard_similarity(mem_words, prop_words)
    score = 0.4 + 0.6 * jacc
    return max(0.0, min(score, 1.0))

# ---------------------------------------------------------
# MASTER SCORING FUNCTION
# ---------------------------------------------------------
def score_proposal(
    message: str,
    proposal: str,
    reasoning_steps: List[str],
    user_emotion: str,
    memory_summary: str,
    all_proposals: List[str],
    actor_name: str = "",
    embed_fn=None,
) -> Dict[str, float]:

    """
    Returns a dict of criterion scores + weighted total.
    """

    # DEBUG: See what emotional state the Jury is receiving
    print("DEBUG user_emotion:", user_emotion)

    scores = {
        "relevance": score_relevance(message, proposal),
        "coherence": score_coherence(proposal),
        "reasoning_quality": score_reasoning_quality(reasoning_steps),
        "intent_alignment": score_intent_alignment(message, proposal, actor_name),

        "emotional_alignment": score_emotional_alignment(
            user_emotion=user_emotion,
            actor_name=actor_name,
            embed_fn=embed_fn
        ),

        "novelty": score_novelty(proposal, all_proposals),
        "memory_alignment": score_memory_alignment(memory_summary, proposal),
    }

    total = sum(scores[k] * RUBRIC_WEIGHTS[k] for k in scores)
    scores["total"] = round(total, 4)
    return scores