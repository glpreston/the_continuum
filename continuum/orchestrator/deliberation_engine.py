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

        self.last_ranked_proposals: List[dict] = []
        self.last_final_proposal: dict | None = None

        log_error("🔥🔥🔥 DELIBERATION ENGINE INITIALIZED 🔥🔥🔥", phase="delib")
        log_debug("[DELIB] Senate + Jury wired into DeliberationEngine", phase="delib")

    # ---------------------------------------------------------
    # MAIN ENTRY POINT (Phase‑4)
    # ---------------------------------------------------------
    def run(
        self,
        controller,
        context: ContinuumContext,
        message: str,
        emotional_state: EmotionalState,
        emotional_memory: EmotionalMemory,
    ) -> Tuple[List[Dict], Dict]:

        log_error("🔥🔥🔥 ENTERED DeliberationEngine.run() 🔥🔥🔥", phase="delib")
        log_info("[DELIB] Starting Senate → Jury pipeline", phase="delib")

        # ---------------------------------------------------------
        # 1. Model selection (Phase‑4)
        # ---------------------------------------------------------
        model = controller.model_selector.select_model(
            message=message,
            emotional_state=emotional_state,
            context=context,
        )

        temperature = controller.temperature
        max_tokens = controller.max_tokens
        system_prompt = controller.system_prompt
        memory = emotional_memory
        voiceprint = controller.voiceprint
        metadata = {}
        telemetry = {}

        # ---------------------------------------------------------
        # 2. Senate deliberation (Phase‑4 signature)
        # ---------------------------------------------------------
        log_error("🔥🔥🔥 CALLING SENATE.deliberate() 🔥🔥🔥", phase="senate")

        ranked_proposals = self.senate.deliberate(
            context=context,
            message=message,
            controller=controller,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            memory=memory,
            emotional_state=emotional_state,
            voiceprint=voiceprint,
            metadata=metadata,
            telemetry=telemetry,
        )

        self.last_ranked_proposals = ranked_proposals

        log_debug(f"[DELIB] Senate produced {len(ranked_proposals)} proposals", phase="senate")
        log_debug(f"[DELIB] Ranked proposals dump: {ranked_proposals}", phase="senate")

        if not ranked_proposals:
            log_error("🔥🔥🔥 ERROR: Senate returned NO proposals 🔥🔥🔥", phase="senate")
            return [], {}

        # ---------------------------------------------------------
        # 3. Jury adjudication
        # ---------------------------------------------------------
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

        log_debug(f"[DELIB] Jury final proposal: {final_proposal}", phase="jury")

        return ranked_proposals, final_proposal