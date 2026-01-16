# continuum/persona/stochastic_variation.py 
from typing import Dict
import random


def apply_stochastic_variation(text: str, style: Dict[str, float]) -> str:
    variants = []

    if style["warmth"] > 1.0:
        variants.append(lambda t: t.replace("Let’s", random.choice([
            "Let’s", "We can", "Together, let’s", "It may help to"
        ]), 1))

    if style["creativity"] > 1.0:
        variants.append(lambda t: t.replace("This suggests", random.choice([
            "This opens the possibility that",
            "This hints at the idea that",
            "One way to see this is that"
        ]), 1))

    if style["softness"] > 1.0:
        variants.append(lambda t: t.replace("We can", random.choice([
            "We can", "We might", "It’s okay if we", "We’re free to"
        ]), 1))

    if variants:
        for fn in random.sample(variants, k=min(2, len(variants))):
            text = fn(text)

    return text