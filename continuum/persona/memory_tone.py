# continuum/personamemory_tone.py  
import re
from typing import Dict


def apply_memory_tone(text: str, memory_mods: Dict[str, float]) -> str:
    if memory_mods.get("warmth_boost", 0) > 0.25:
        text = re.sub(r"\bLet’s\b", "Let’s take a bright look at this and", text, count=1)
        text = text.replace("This suggests", "This opens up the sense that")

    if memory_mods.get("pacing_slowdown", 0) > 0.15 and "\n\n" not in text:
        text = re.sub(r"\. (?=[A-Z])", ".\n\n", text)
        text = re.sub(r"\bLet’s\b", "We can move gently as we", text, count=1)

    if memory_mods.get("grounding_boost", 0) > 0.25:
        text = text.replace("clearly", "steadily")
        text = text.replace("notably", "meaningfully")

    return text