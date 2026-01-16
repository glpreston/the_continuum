# continuum/rubric/__init__.py
"""
Rubric 3.0 module package.
Provides modular scoring components for the Jury system.
"""

from .semantic import score_semantic_relevance, score_semantic_depth
from .structure import score_structure
from .emotion import score_emotional_alignment
from .context import (
    score_memory_alignment,
    score_novelty,
    compute_contextual_weights,
    apply_persona_curve,
)