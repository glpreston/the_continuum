# continuum/emotion/emotional_momentum.py

from typing import Dict, List, Any


def apply_emotional_momentum(
    fusion_weights: Dict[str, float],
    emotional_arc_history: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Adjust fusion weights based on recent emotional momentum.
    """
    if len(emotional_arc_history) < 3 or not fusion_weights:
        return fusion_weights

    def slope(key: str, window: int = 3) -> float:
        start = emotional_arc_history[-window]["state"].get(key, 0.0)
        end = emotional_arc_history[-1]["state"].get(key, 0.0)
        return end - start

    curiosity_s = slope("curiosity")
    tension_s = slope("tension")
    calm_s = slope("calm")
    fatigue_s = slope("fatigue")

    adjusted = fusion_weights.copy()

    # Rising curiosity → more Storyweaver + Analyst
    if curiosity_s > 0.05:
        adjusted["senate_storyweaver"] = adjusted.get("senate_storyweaver", 0.0) + 0.05
        adjusted["senate_analyst"] = adjusted.get("senate_analyst", 0.0) + 0.03

    # Rising tension → more Synthesizer + Architect
    if tension_s > 0.05:
        adjusted["senate_synthesizer"] = adjusted.get("senate_synthesizer", 0.0) + 0.05
        adjusted["senate_architect"] = adjusted.get("senate_architect", 0.0) + 0.03

    # Settling calm → more Synthesizer
    if calm_s > 0.05:
        adjusted["senate_synthesizer"] = adjusted.get("senate_synthesizer", 0.0) + 0.04

    # Rising fatigue → reduce high‑verbosity actors
    if fatigue_s > 0.03:
        adjusted["senate_storyweaver"] = adjusted.get("senate_storyweaver", 0.0) - 0.04

    # Normalize
    total = sum(max(v, 0.0) for v in adjusted.values()) or 1.0
    for k in adjusted:
        adjusted[k] = max(adjusted[k], 0.0) / total

    return adjusted