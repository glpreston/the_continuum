# continuum/orchestrator/fusion_pipeline.py

from typing import Dict, List, Optional
from continuum.core.logger import log_info, log_debug, log_error

from continuum.orchestrator.fusion_smoothing import FusionSmoother
from continuum.emotion.emotional_momentum import apply_emotional_momentum
from continuum.orchestrator.fusion_engine import fused_response


class FusionPipeline:
    """
    Fusion Pipeline (patched for MAX‑HYBRID Fusion)
      - smoothing
      - depth boost
      - emotional momentum
      - fused multi‑actor response
      - clean fallback path
    """

    def __init__(self, smoother: FusionSmoother, emotional_arc_engine):
        self.smoother = smoother
        self.emotional_arc_engine = emotional_arc_engine

        # Debug traces
        self.last_raw_weights: Dict[str, float] = {}
        self.last_smoothed_weights: Dict[str, float] = {}
        self.last_final_text: Optional[str] = None

    # ---------------------------------------------------------
    # APPLY SMOOTHING + EMOTIONAL MOMENTUM + DEPTH BOOST
    # ---------------------------------------------------------
    def adjust(self, final_proposal: Dict) -> Dict[str, float]:
        """
        Extracts fusion weights from the final proposal and applies:
          - smoothing
          - depth-aware boost (semantic depth + structure)
          - emotional momentum
        """

        metadata = final_proposal.get("metadata", {}) or {}
        raw_weights = metadata.get("fusion_weights", {}) or {}
        self.last_raw_weights = raw_weights

        log_info("Applying fusion smoothing and emotional momentum", phase="fusion")

        # Step 1: smoothing
        smoothed = self.smoother.smooth(raw_weights)
        self.last_smoothed_weights = smoothed

        # Step 1.5: depth-aware boost
        jury_all_scores = metadata.get("jury_all_scores", {}) or {}

        depth_boosted: Dict[str, float] = {}
        for actor_name, weight in smoothed.items():
            actor_scores = jury_all_scores.get(actor_name, {}) or {}
            semantic_depth = actor_scores.get("semantic_depth", 0.0)
            structure_score = actor_scores.get("structure", 0.0)

            depth_factor = 1.0 + 0.35 * semantic_depth + 0.20 * structure_score
            depth_boosted[actor_name] = weight * depth_factor

        # Renormalize
        total_boosted = sum(depth_boosted.values()) or 1.0
        depth_boosted = {k: v / total_boosted for k, v in depth_boosted.items()}

        log_debug(
            f"Fusion weights after depth boost: {depth_boosted}",
            phase="fusion",
        )

        # Step 2: emotional momentum
        adjusted = apply_emotional_momentum(
            depth_boosted,
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
          - fused multi‑actor response (if weights exist)
          - fallback single‑actor path (if no weights)
        """

        print("\n>>> ENTERED FusionPipeline.run() <<<")

        # -----------------------------------------------------
        # 1. If no fusion weights → fallback to Jury winner
        # -----------------------------------------------------
        if not fusion_weights or sum(fusion_weights.values()) == 0:
            print(">>> NO FUSION WEIGHTS — FALLBACK TO SINGLE ACTOR <<<")

            if not ranked_proposals:
                log_error("No ranked proposals available.", phase="fusion")
                return "The Continuum encountered an error: no proposals available."

            top = ranked_proposals[0]
            controller.last_final_proposal = top
            return top.get("content", "")

        # -----------------------------------------------------
        # 2. Otherwise → call MAX‑HYBRID fused_response()
        # -----------------------------------------------------
        print(">>> CALLING fused_response() — MAX‑HYBRID MODE ACTIVE <<<")

        final_text = fused_response(
            fusion_weights=fusion_weights,
            ranked_proposals=ranked_proposals,
            controller=controller,
        )

        # Ensure last_final_proposal is set
        if not controller.last_final_proposal:
            controller.last_final_proposal = ranked_proposals[0]

        self.last_final_text = final_text
        return final_text