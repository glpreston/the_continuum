# continuum/orchestrator/deliberation_engine.py

from typing import List, Dict, Tuple
from continuum.core.logger import log_info, log_debug, log_error

from continuum.emotion.state_machine import EmotionalState
from continuum.persona.emotional_memory import EmotionalMemory
from continuum.core.context import ContinuumContext

from continuum.orchestrator.senate import Senate
from continuum.orchestrator.jury import Jury


class DeliberationEngine:
    """
    Encapsulates the Senate → Jury pipeline.
    Produces:
      - ranked proposals from Senate
      - final proposal from Jury
    """

    def __init__(self, senate: Senate, jury: Jury):
        self.senate = senate
        self.jury = jury

        # Debug traces
        self.last_ranked_proposals: List[dict] = []
        self.last_final_proposal: dict | None = None

    # ---------------------------------------------------------
    # MAIN ENTRY POINT
    # ---------------------------------------------------------
    def run(
        self,
        controller,                     # <-- added
        context: ContinuumContext,
        message: str,
        emotional_state: EmotionalState,
        emotional_memory: EmotionalMemory,
    ) -> Tuple[List[Dict], Dict]:
        """
        Executes:
          1. Senate deliberation
          2. Jury adjudication
        Returns:
          ranked_proposals, final_proposal
        """

        # -------------------------
        # 1. Senate deliberation
        # -------------------------
        log_info("Starting Senate deliberation", phase="senate")

        ranked_proposals = self.senate.deliberate(
            context=context,
            message=message,
            controller=controller,       # <-- FIXED: pass real controller
            emotional_state=emotional_state,
            emotional_memory=emotional_memory,
        )

        self.last_ranked_proposals = ranked_proposals

        log_debug(
            f"Senate produced {len(ranked_proposals)} proposals",
            phase="senate",
        )

        if not ranked_proposals:
            log_error("Senate returned no proposals", phase="senate")
            return [], {}

        # -------------------------
        # 2. Jury adjudication
        # -------------------------
        log_info("Starting Jury adjudication", phase="jury")

        final_proposal = self.jury.adjudicate(
            ranked_proposals,
            message=message,
            user_emotion=emotional_memory.get_smoothed_state(),
            memory_summary=context.get_memory_summary(),
            emotional_state=EmotionalState.from_dict(emotional_state.as_dict()),
        )

        self.last_final_proposal = final_proposal

        log_debug(
            f"Jury selected proposal from actor={final_proposal.get('actor')}",
            phase="jury",
        )

        return ranked_proposals, final_proposal