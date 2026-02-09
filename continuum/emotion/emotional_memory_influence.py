# continuum/emotion/emotional_memory_influence.py

from __future__ import annotations
from typing import Dict, Any, List


def _extract_recent_events(emotional_memory, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Safely extract the most recent emotional events from EI‑2.0 emotional memory.
    Assumes emotional_memory exposes a `.events` list or similar iterable.
    """
    events = getattr(emotional_memory, "events", []) or []
    return list(events)[-limit:]


def _aggregate_emotions(events: List[Any]) -> Dict[str, float]:
    """
    Aggregate emotion intensities across recent events.
    Works with EmotionalEvent objects (EI‑2.0).
    """
    totals: Dict[str, float] = {}
    count = 0

    for ev in events:
        # EmotionalEvent.raw_state is already a dict
        raw = getattr(ev, "raw_state", None)
        if not isinstance(raw, dict):
            continue

        count += 1
        for k, v in raw.items():
            totals[k] = totals.get(k, 0.0) + float(v)

    if count == 0:
        return {}

    # Normalize by number of events
    return {k: v / count for k, v in totals.items()}

def _compute_fatigue_score(agg: Dict[str, float]) -> float:
    """
    Heuristic fatigue score based on repeated sadness / confusion / tension‑like states.
    """
    sadness = agg.get("sadness", 0.0)
    confusion = agg.get("confusion", 0.0)
    grief = agg.get("grief", 0.0)
    nervousness = agg.get("nervousness", 0.0)

    # Simple bounded sum
    raw = sadness * 0.5 + confusion * 0.3 + grief * 0.4 + nervousness * 0.2
    return min(raw, 1.0)


def _compute_curiosity_persistence(agg: Dict[str, float]) -> float:
    """
    How strongly curiosity has persisted across recent turns.
    """
    curiosity = agg.get("curiosity", 0.0)
    neutral = agg.get("neutral", 0.0)

    raw = curiosity * 0.7 + neutral * 0.2
    return min(raw, 1.0)


def emotional_memory_modifiers(emotional_memory) -> Dict[str, float]:
    """
    Step F‑1: Derive coarse modifiers from emotional memory.

    These modifiers are NOT the final style values, but hints that the
    Meta‑Persona can use to adjust warmth, grounding, clarity, and pacing.
    """
    events = _extract_recent_events(emotional_memory, limit=10)
    if not events:
        return {
            "fatigue_boost": 0.0,
            "warmth_boost": 0.0,
            "grounding_boost": 0.0,
            "clarity_boost": 0.0,
            "pacing_slowdown": 0.0,
            "curiosity_persistence": 0.0,
        }

    agg = _aggregate_emotions(events)
    fatigue = _compute_fatigue_score(agg)
    curiosity_persist = _compute_curiosity_persistence(agg)

    # Map to simple 0–0.4 style nudges
    fatigue_boost = min(fatigue * 0.4, 0.4)
    warmth_boost = min((fatigue + curiosity_persist) * 0.3, 0.4)
    grounding_boost = min(fatigue * 0.35, 0.4)
    clarity_boost = min((agg.get("confusion", 0.0) + fatigue) * 0.3, 0.4)
    pacing_slowdown = min(fatigue * 0.5, 0.5)

    return {
        "fatigue_boost": round(fatigue_boost, 3),
        "warmth_boost": round(warmth_boost, 3),
        "grounding_boost": round(grounding_boost, 3),
        "clarity_boost": round(clarity_boost, 3),
        "pacing_slowdown": round(pacing_slowdown, 3),
        "curiosity_persistence": round(curiosity_persist, 3),
    }