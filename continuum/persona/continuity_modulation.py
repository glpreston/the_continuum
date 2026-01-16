# continuum/personacontinuity_modulation.py 

from typing import Dict, List, Any


def apply_continuity_modulation(
    text: str,
    volatility: float,
    confidence: float,
    arc_label: str,
    style: Dict[str, float],
) -> str:
    tone_modifiers: List[str] = []

    if volatility > 0.25:
        tone_modifiers.append("Keep sentences short and stabilizing.")

    if confidence < 0.4:
        tone_modifiers.append("Use a warm, reassuring tone.")

    if "Curiosity" in arc_label:
        tone_modifiers.append("Lean into exploratory, imaginative language.")
    elif "Tension" in arc_label:
        tone_modifiers.append("Be calming, structured, and steady.")
    elif "Calm" in arc_label:
        tone_modifiers.append("Maintain a smooth, flowing narrative.")
    elif "Recovery" in arc_label:
        tone_modifiers.append("Acknowledge progress and reinforce stability.")

    if volatility > 0.3:
        style["brevity"] += 0.2

    if confidence < 0.4:
        style["softness"] += 0.2

    modifier_text = " ".join(tone_modifiers).strip()
    if modifier_text:
        # Add a trailing period so it’s a complete sentence and less likely to be rewritten oddly
        if not modifier_text.endswith("."):
            modifier_text += "."
        text = f"{modifier_text} {text}"

    return text