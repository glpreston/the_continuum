# continuum/emotion/jury_adaptive_weights.py

from typing import Dict
from continuum.emotion.state_machine import EmotionalState


def compute_adaptive_weights(state: EmotionalState) -> Dict[str, float]:
    """
    Convert emotional state → dynamic Jury weight adjustments.
    Depth‑aware Rubric 3.0 version:
      - relevance
      - semantic_depth
      - structure
      - emotional_alignment
      - memory_alignment
      - novelty
    """

    s = state.as_dict()

    # ---------------------------------------------------------
    # Depth‑aware base weights
    # ---------------------------------------------------------
    # These ensure the Jury always prioritizes depth + structure,
    # even before emotional modulation is applied.
    weights = {
        "relevance": 1.0,
        "semantic_depth": 1.6,   # strong base emphasis
        "structure": 1.3,        # moderate base emphasis
        "emotional_alignment": 0.8,
        "memory_alignment": 0.7,
        "novelty": 0.6,
        "integrative_reasoning": 1.2,  # NEW
    }

    # ---------------------------------------------------------
    # Emotional influences (gentle, not dominant)
    # ---------------------------------------------------------

    # Structure increases with tension (need for clarity) and calm (stability)
    weights["structure"] += s["tension"] * 0.25 + s["calm"] * 0.15

    # Semantic depth increases with focus + calm
    weights["semantic_depth"] += s["focus"] * 0.35 + s["calm"] * 0.25

    # Relevance increases slightly with fatigue (need for grounding)
    weights["relevance"] += s["fatigue"] * 0.15

    # Emotional alignment responds to joy + tension, but gently
    weights["emotional_alignment"] += s["joy"] * 0.20 + s["tension"] * 0.10

    # Novelty responds to curiosity + joy
    weights["novelty"] += s["curiosity"] * 0.25 + s["joy"] * 0.10

    # Memory alignment increases with calm (stability)
    weights["memory_alignment"] += s["calm"] * 0.15

    # Integrative reasoning increases with curiosity, calm, and focus
    weights["integrative_reasoning"] += (
        s["curiosity"] * 0.30
        + s["calm"] * 0.20
        + s["focus"] * 0.25
    )

    # ---------------------------------------------------------
    # Normalize to stable range
    # ---------------------------------------------------------
    for k in weights:
        weights[k] = max(0.5, min(2.0, weights[k]))

    return weights