# continuum/persona/continuity_modulation.py

from typing import Dict, List, Any

def apply_continuity_modulation(
    text: str,
    volatility: float,
    confidence: float,
    arc_label: str,
    style: Dict[str, float],
) -> str:
    """
    Fusion 2.1: continuity modulation should adjust style parameters only.
    It must NOT prepend sentences or inject instructional text.
    """

    # Adjust style weights only — no text injection
    if volatility > 0.3:
        style["brevity"] += 0.2

    if confidence < 0.4:
        style["softness"] += 0.2

    # Optional: arc-based style nudges (no text added)
    if "Curiosity" in arc_label:
        style["creativity"] += 0.1
    elif "Tension" in arc_label:
        style["clarity"] += 0.1
    elif "Calm" in arc_label:
        style["smoothness"] = style.get("smoothness", 0) + 0.1
    elif "Recovery" in arc_label:
        style["warmth"] += 0.1

    return text