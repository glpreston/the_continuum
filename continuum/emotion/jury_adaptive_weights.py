# continuum/emotion/jury_adaptive_weights.py

from typing import Dict
from continuum.emotion.state_machine import EmotionalState


def compute_adaptive_weights(state: EmotionalState) -> Dict[str, float]:
    """
    Convert emotional state → dynamic Jury weight adjustments.
    Rubric 3.0 version:
      - relevance
      - semantic_depth
      - structure
      - emotional_alignment
      - memory_alignment
      - novelty
    """

    s = state.as_dict()

    # ---------------------------------------------------------
    # Base weights (Rubric 3.0)
    # ---------------------------------------------------------
    weights = {
        "relevance": 1.0,
        "semantic_depth": 1.0,
        "structure": 1.0,
        "emotional_alignment": 1.0,
        "memory_alignment": 1.0,
        "novelty": 1.0,
    }

    # ---------------------------------------------------------
    # Emotional influences (mapped from old → new dimensions)
    # ---------------------------------------------------------

    # Structure ~ old "coherence"
    weights["structure"] += s["tension"] * 0.4 + s["calm"] * 0.2

    # Semantic depth ~ old "reasoning_quality"
    weights["semantic_depth"] += s["focus"] * 0.5 + s["calm"] * 0.3

    # Relevance ~ old "relevance" + fatigue bias
    weights["relevance"] += s["fatigue"] * 0.3

    # Emotional alignment (unchanged)
    weights["emotional_alignment"] += s["joy"] * 0.4 + s["tension"] * 0.2

    # Novelty (unchanged)
    weights["novelty"] += s["curiosity"] * 0.5 + s["joy"] * 0.2

    # Memory alignment (unchanged)
    weights["memory_alignment"] += s["calm"] * 0.2

    # ---------------------------------------------------------
    # Normalize to stable range
    # ---------------------------------------------------------
    for k in weights:
        weights[k] = max(0.5, min(2.0, weights[k]))

    return weights