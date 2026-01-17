# continuum/emotion/emotional_state_manager.py

from typing import Dict
from continuum.core.logger import log_debug
from continuum.emotion.mappings import build_delta_from_labels
from continuum.emotion.state_machine import (
    update_emotional_state,
    EmotionalState,
)


class EmotionalStateManager:
    """
    Handles emotional state updates:
      - builds deltas from raw emotion labels
      - updates the EmotionalState object
      - logs transitions
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # MAIN UPDATE ENTRY POINT
    # ---------------------------------------------------------
    def update(self, current_state: EmotionalState, raw_state: Dict[str, float]) -> EmotionalState:
        """
        Given the current emotional state and raw emotion scores,
        compute the delta and update the emotional state.
        """

        # Convert raw labels → delta vector
        delta = build_delta_from_labels(raw_state)

        # Update emotional state using the state machine
        new_state = update_emotional_state(current_state, delta)

        log_debug(
            f"Emotional state updated: {new_state.as_dict()}",
            phase="emotion",
        )

        return new_state