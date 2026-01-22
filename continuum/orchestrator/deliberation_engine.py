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

        log_error("🔥🔥🔥 DELIBERATION ENGINE INITIALIZED 🔥🔥🔥", phase="delib")
        log_debug("[DELIB] Senate + Jury wired into DeliberationEngine", phase="delib")

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
        # ENTRY MARKER
        # -------------------------
        log_error("🔥🔥🔥 ENTERED DeliberationEngine.run() 🔥🔥🔥", phase="delib")
        log_info("[DELIB] Starting Senate → Jury pipeline", phase="delib")

        # -------------------------
        # 1. Senate deliberation
        # -------------------------
        log_error("🔥🔥🔥 CALLING SENATE.deliberate() 🔥🔥🔥", phase="senate")

        ranked_proposals = self.senate.deliberate(
            context=context,
            message=message,
            controller=controller,       # <-- FIXED: pass real controller
            emotional_state=emotional_state,
            emotional_memory=emotional_memory,
        )

        self.last_ranked_proposals = ranked_proposals

        # --- DEBUG: Senate output ---
        log_debug(
            f"[DELIB] Senate produced {len(ranked_proposals)} proposals",
            phase="senate",
        )
        log_debug(
            f"[DELIB] Ranked proposals dump: {ranked_proposals}",
            phase="senate",
        )
        # ----------------------------

        if not ranked_proposals:
            log_error("🔥🔥🔥 ERROR: Senate returned NO proposals 🔥🔥🔥", phase="senate")
            return [], {}

        # -------------------------
        # 2. Jury adjudication
        # -------------------------
        log_error("🔥🔥🔥 CALLING JURY.adjudicate() 🔥🔥🔥", phase="jury")
        log_info("[DELIB] Starting Jury adjudication", phase="jury")

        final_proposal = self.jury.adjudicate(
            ranked_proposals,
            message=message,
            user_emotion=emotional_memory.get_smoothed_state(),
            memory_summary=context.get_memory_summary(),
            emotional_state=EmotionalState.from_dict(emotional_state.as_dict()),
        )

        self.last_final_proposal = final_proposal

        # --- DEBUG: Jury output ---
        log_debug(
            f"[DELIB] Jury final proposal: {final_proposal}",
            phase="jury",
        )

        metadata = final_proposal.get("metadata", {})
        fusion_weights = metadata.get("fusion_weights", None)

        log_debug(
            f"[DELIB] Final proposal metadata: {metadata}",
            phase="jury",
        )
        log_debug(
            f"[DELIB] Extracted fusion_weights: {fusion_weights}",
            phase="jury",
        )

        # Fusion weight warnings
        if fusion_weights is None:
            log_error(
                "🔥🔥🔥 WARNING: final_proposal contains NO fusion_weights field! 🔥🔥🔥",
                phase="jury",
            )
        elif fusion_weights == {}:
            log_error(
                "🔥🔥🔥 WARNING: fusion_weights is EMPTY {} — Fusion will fallback or fail. 🔥🔥🔥",
                phase="jury",
            )

        # ---------------------------
        # RETURN
        # ---------------------------
        log_error("🔥🔥🔥 DELIBERATION ENGINE RETURNING RESULTS 🔥🔥🔥", phase="delib")
        return ranked_proposals, final_proposal