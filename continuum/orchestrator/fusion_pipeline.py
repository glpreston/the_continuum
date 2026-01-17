# continuum/orchestrator/fusion_pipeline.py

from typing import Dict, List, Optional
from continuum.core.logger import log_info, log_debug, log_error

from continuum.orchestrator.fusion_smoothing import FusionSmoother
from continuum.emotion.emotional_momentum import apply_emotional_momentum
from continuum.orchestrator.fusion_engine import fused_response


class FusionPipeline:
    """
    Encapsulates Fusion 2.0:
      - smoothing
      - emotional momentum
      - fused multi-actor response
      - fallback single-actor path
    """

    def __init__(self, smoother: FusionSmoother, emotional_arc_engine):
        self.smoother = smoother
        self.emotional_arc_engine = emotional_arc_engine

        # Debug traces
        self.last_raw_weights: Dict[str, float] = {}
        self.last_smoothed_weights: Dict[str, float] = {}
        self.last_final_text: Optional[str] = None

    # ---------------------------------------------------------
    # APPLY SMOOTHING + EMOTIONAL MOMENTUM
    # ---------------------------------------------------------
    def adjust(self, final_proposal: Dict) -> Dict[str, float]:
        """
        Extracts fusion weights from the final proposal and applies:
          - smoothing
          - emotional momentum
        Returns adjusted weights.
        """

        raw_weights = final_proposal.get("metadata", {}).get("fusion_weights", {})
        self.last_raw_weights = raw_weights

        log_info("Applying fusion smoothing and emotional momentum", phase="fusion")

        # Step 1: smoothing
        smoothed = self.smoother.smooth(raw_weights or {})
        self.last_smoothed_weights = smoothed

        # Step 2: emotional momentum
        adjusted = apply_emotional_momentum(
            smoothed or {},
            self.emotional_arc_engine.get_history(),
        )

        log_debug(
            f"Fusion weights after smoothing/momentum: {adjusted}",
            phase="fusion",
        )

        return adjusted

    # ---------------------------------------------------------
    # RUN FUSION OR FALLBACK
    # ---------------------------------------------------------
    def run(
        self,
        fusion_weights: Dict[str, float],
        ranked_proposals: List[Dict],
        controller,
    ) -> str:
        """
        Executes:
          - fused multi-actor response (if weights exist)
          - fallback single-actor path (if no weights)
        """

        # -------------------------
        # FUSED RESPONSE
        # -------------------------
        if fusion_weights:
            log_info("Running fused response", phase="fusion")

            final_text = fused_response(
                fusion_weights=fusion_weights,
                ranked_proposals=ranked_proposals,
                controller=controller,
            )

            self.last_final_text = final_text
            return final_text

        # -------------------------
        # FALLBACK: SINGLE ACTOR
        # -------------------------
        log_info("Fusion weights empty — using single actor path", phase="fusion")

        final_proposal = ranked_proposals[0]
        actor_name = final_proposal.get("actor")
        llm_name = controller.senate_to_llm_map.get(actor_name, actor_name)
        actor = controller.actors.get(llm_name)

        if not actor:
            log_error(
                f"Unknown actor during fallback fusion path: {llm_name}",
                phase="fusion",
            )
            return "The Continuum encountered an error: unknown actor."

        final_text = actor.respond(
            context=controller.context,
            selected_proposal=final_proposal,
            emotional_memory=controller.emotional_memory,
            emotional_state=controller.emotional_state,
        )

        self.last_final_text = final_text
        return final_text
    