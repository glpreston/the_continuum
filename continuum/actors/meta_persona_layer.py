"""
Meta‑persona blending layer.
Transforms actor proposals into a unified stylistic tone
based on the Continuum's persona traits.
"""

from __future__ import annotations
from typing import List

from continuum.config.personas import PersonaTrait


def blend_traits(traits: List[PersonaTrait]) -> str:
    """
    Produce a short stylistic hint based on weighted traits.
    This keeps the unified voice expressive but compact.
    """
    if not traits:
        return "neutral and concise"

    # Weighted summary of traits
    sorted_traits = sorted(traits, key=lambda t: t.weight, reverse=True)
    top = sorted_traits[0]

    return f"{top.description.lower()}"


def apply_meta_style(text: str, traits: List[PersonaTrait]) -> str:
    """
    Apply a subtle stylistic transformation to a proposal.
    This keeps the system's voice coherent without being heavy‑handed.
    """
    style = blend_traits(traits)
    return f"{text} (styled with {style})"