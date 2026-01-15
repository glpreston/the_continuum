# continuum/emotion/jury_adaptive_weights.py

from typing import Dict
from continuum.emotion.state_machine import EmotionalState


def compute_adaptive_weights(state: EmotionalState) -> Dict[str, float]:
    """
    Convert emotional state → dynamic Jury weight adjustments.
    All values are gentle biases, not hard overrides.
    """

    s = state.as_dict()

    # Base weights (Rubric 4.0)
    weights = {
        "relevance": 1.0,
        "coherence": 1.0,
        "reasoning_quality": 1.0,
        "intent_alignment": 1.0,
        "emotional_alignment": 1.0,
        "novelty": 1.0,
        "memory_alignment": 1.0,
    }

    # Emotional influences
    weights["coherence"] += s["tension"] * 0.4 + s["calm"] * 0.2
    weights["intent_alignment"] += s["tension"] * 0.3 + s["confidence"] * 0.2
    weights["novelty"] += s["curiosity"] * 0.5 + s["joy"] * 0.2
    weights["reasoning_quality"] += s["focus"] * 0.5 + s["calm"] * 0.3
    weights["emotional_alignment"] += s["joy"] * 0.4 + s["tension"] * 0.2
    weights["relevance"] += s["fatigue"] * 0.3
    weights["memory_alignment"] += s["calm"] * 0.2

    # Normalize so weights stay in a stable range
    for k in weights:
        weights[k] = max(0.5, min(2.0, weights[k]))

    return weights