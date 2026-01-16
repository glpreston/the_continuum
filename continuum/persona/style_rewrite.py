# continuum/personastyle_rewrite.py  

import re
from typing import Dict


def apply_style(text: str, style: Dict[str, float]) -> str:
    warmth = style["warmth"]
    clarity = style["clarity"]
    brevity = style["brevity"]
    creativity = style["creativity"]
    softness = style["softness"]

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