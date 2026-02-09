# continuum/persona/style_rewrite.py

from typing import Dict, Any
from .voiceprints import SystemVoiceprint
from continuum.core.logger import log_debug
import re

def old_apply_style(text, style):
    # Provide safe defaults if style is missing or incomplete
    style = style or {}

    warmth = style.get("warmth", 0.5)
    clarity = style.get("clarity", 0.5)
    depth = style.get("depth", 0.5)
    cadence = style.get("cadence", 0.5)
    metaphor_density = style.get("metaphor_density", 0.5)
    brevity = style.get("brevity", 0.5)
    creativity = style.get("creativity", 0.5)   
    softness = style.get("softness", 0.5)

    if warmth > 1.1:
        text = text.replace("I interpret this as", "I understand this as")
        text = text.replace("Here is", "Let’s explore")

    if clarity > 1.1:
        # Only replace standalone "and" not already followed by "also"
        text = re.sub(r"\band\b(?! also)", "and also", text)

    if brevity > 1.1:
        words = text.split()
        if len(words) > 140:
            text = " ".join(words[:140]) + "..."

    if creativity > 1.1:
        text = text.replace("integrated perspective", "woven perspective")
        text = text.replace("common ground", "shared horizon")

    if softness > 1.1:
        text = text.replace("resolve tensions", "ease the strain")
        text = text.replace("unified path", "gentle next step")

    return text

# continuum/persona/style_rewrite.py

def apply_style(
    text: str,
    style: Dict[str, float],
    system_voiceprint: SystemVoiceprint | None = None,
) -> str:
    """
    Applies high-level style shaping:
      - pacing
      - density
      - grounding
      - metaphor density
      - softening / crispness
      - continuity / warmth_curve (if v2.0)
    """

    if system_voiceprint is None:
        return text  # legacy fallback

    params = system_voiceprint.emotional_rewrite_parameters
    global_weights = params["global_weights"]

    log_debug(
        "[AIRA][style_rewrite] Applying style with SystemVoiceprint "
        f"version={system_voiceprint.version}, global_weights={global_weights}"
    )

    # You can blend `style` (from compute_aria_style) with voiceprint weights here.
    # For now, we just log and return text unchanged to keep behavior stable.
    
    return text