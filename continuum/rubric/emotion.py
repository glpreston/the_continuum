# continuum/rubric/emotion.py
"""
Emotional Scoring — Jury Rubric 3.0
-----------------------------------

Evaluates:
- Emotional alignment between user emotional state and actor persona
- EI‑2.0 emotional resonance (dominant emotion, smoothed state)
- Volatility shaping (high volatility → softer scoring)
- Confidence shaping (stronger signals → stronger alignment)

All scores normalized to [0, 1].
"""

from typing import Dict, Optional, List
import math


# =========================================================
# Persona Emotional Profiles (LLM‑native)
# =========================================================

PERSONA_EMOTIONAL_PROFILES = {
    "SenateAnalyst": "neutral, objective, steady, logical",
    "SenateArchitect": "calm, structured, methodical, grounded",
    "SenateSynthesizer": "balanced, empathetic, integrative, warm",
    "SenateStoryweaver": "expressive, emotional, imaginative, heartfelt",
}


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
# Emotional Alignment (EI‑2.0 aware)
# =========================================================

def score_emotional_alignment(
    user_emotion,
    actor_name: str,
    embed_fn=None,
) -> float:
    """
    Computes emotional alignment between:
    - the user's emotional state (EI‑2.0 dict or legacy string)
    - the actor's persona emotional profile

    Uses embeddings when available.
    """

    # -----------------------------
    # 1. Actor persona profile
    # -----------------------------
    persona_profile = PERSONA_EMOTIONAL_PROFILES.get(actor_name, "")
    if not persona_profile or embed_fn is None:
        return 0.5  # neutral fallback

    persona_emb = embed_fn(persona_profile)

    # -----------------------------
    # 2. Legacy string emotion
    # -----------------------------
    if isinstance(user_emotion, str):
        if not user_emotion:
            return 0.5
        user_emb = embed_fn(user_emotion)
        if not user_emb:
            return 0.5
        sim = _cosine(user_emb, persona_emb)
        return (sim + 1) / 2  # normalize to [0, 1]

    # -----------------------------
    # 3. EI‑2.0 emotional dict
    # -----------------------------
    if not isinstance(user_emotion, dict):
        return 0.5

    smoothed = user_emotion.get("smoothed_state", {}) or {}
    dominant = user_emotion.get("dominant_emotion", None)
    confidence = float(user_emotion.get("confidence", 0.0) or 0.0)
    volatility = float(user_emotion.get("volatility", 0.0) or 0.0)

    # Build emotional text representation
    parts = []
    if dominant:
        parts.append(f"dominant: {dominant}")
    for dim, val in smoothed.items():
        parts.append(f"{dim}: {val:.3f}")

    emo_text = "; ".join(parts) if parts else "neutral"
    user_emb = embed_fn(emo_text)

    if not user_emb:
        return 0.5

    # Base similarity
    base = (_cosine(user_emb, persona_emb) + 1) / 2

    # Volatility shaping (high volatility → softer alignment)
    volatility_factor = 1.0 / (1.0 + volatility)

    # Confidence shaping (stronger signals → stronger alignment)
    confidence_factor = 0.5 + 0.5 * confidence

    score = base * volatility_factor * confidence_factor
    return max(0.0, min(score, 1.0))