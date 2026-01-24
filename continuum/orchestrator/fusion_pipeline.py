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
    # APPLY SMOOTHING + EMOTIONAL MOMENTUM + DEPTH BOOST
    # ---------------------------------------------------------
    def adjust(self, final_proposal: Dict) -> Dict[str, float]:
        """
        Extracts fusion weights from the final proposal and applies:
          - smoothing
          - depth-aware boost (semantic depth from Jury)
          - emotional momentum
        Returns adjusted weights.
        """

        metadata = final_proposal.get("metadata", {}) or {}
        raw_weights = metadata.get("fusion_weights", {}) or {}
        self.last_raw_weights = raw_weights

        log_info("Applying fusion smoothing and emotional momentum", phase="fusion")

        # Step 1: smoothing
        smoothed = self.smoother.smooth(raw_weights)
        self.last_smoothed_weights = smoothed

        # -----------------------------------------------------
        # Step 1.5: depth-aware boost using Jury scores
        # -----------------------------------------------------
        jury_all_scores = metadata.get("jury_all_scores", {}) or {}

        depth_boosted: Dict[str, float] = {}
        for actor_name, weight in smoothed.items():
            actor_scores = jury_all_scores.get(actor_name, {}) or {}
            semantic_depth = actor_scores.get("semantic_depth", 0.0)
            structure_score = actor_scores.get("structure", 0.0)

            # Depth factor: reward deeper + better structured proposals
            # semantic_depth is typically in [0, 1]; structure in [0, 1]
            depth_factor = 1.0 + 0.35 * semantic_depth + 0.20 * structure_score

            boosted_weight = weight * depth_factor
            depth_boosted[actor_name] = boosted_weight

        # Renormalize after boosting so weights sum to ~1
        total_boosted = sum(depth_boosted.values()) or 1.0
        depth_boosted = {
            k: v / total_boosted for k, v in depth_boosted.items()
        }

        log_debug(
            f"Fusion weights after depth boost (semantic_depth + structure): {depth_boosted}",
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
        log_debug(
            f"[FUSION FALLBACK] fusion_weights empty. Ranked proposals: {ranked_proposals}",
            phase="fusion",
        )

        if not ranked_proposals:
            log_error(
                "[FUSION FALLBACK] No ranked proposals available.",
                phase="fusion",
            )
            return "The Continuum encountered an error: no proposals available."

        first = ranked_proposals[0]
        log_debug(
            f"[FUSION FALLBACK] First proposal actor: {first.get('actor')}",
            phase="fusion",
        )

        log_info("Fusion weights empty — using single actor path", phase="fusion")

        final_proposal = first
        actor_name = final_proposal.get("actor")
        llm_name = controller.senate_to_llm_map.get(actor_name, actor_name)
        actor = controller.actors.get(llm_name)

        log_debug(
            f"[FUSION FALLBACK] Using actor '{llm_name}' for fallback generation.",
            phase="fusion",
        )

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

        log_debug(
            f"[FUSION FALLBACK] Actor returned text: {final_text}",
            phase="fusion",
        )

        self.last_final_text = final_text
        return final_text