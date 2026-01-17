# continuum/core/turn_logger.py

from typing import Dict, Any, List
from continuum.core.logger import log_debug


class TurnLogger:
    """
    Handles turn-by-turn logging for The Continuum.
    Stores:
      - user message
      - detected emotion
      - final proposal
      - assistant output
    """

    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # APPEND TURN
    # ---------------------------------------------------------
    def append(
        self,
        user_message: str,
        assistant_output: str,
        raw_emotion: Dict[str, float],
        final_proposal: Dict[str, Any],
        dominant_emotion: str,
        intensity: float,
    ):
        """
        Appends a single turn to the history.
        """

        entry = {
            "user": user_message,
            "emotion": {
                "dominant": dominant_emotion,
                "intensity": intensity,
                "raw_state": raw_emotion,
            },
            "final_proposal": final_proposal,
            "assistant": assistant_output,
        }

        self.history.append(entry)

        log_debug("Turn appended to history", phase="pipeline")

    # ---------------------------------------------------------
    # GET FULL HISTORY
    # ---------------------------------------------------------
    def get_history(self) -> List[Dict[str, Any]]:
        return self.history