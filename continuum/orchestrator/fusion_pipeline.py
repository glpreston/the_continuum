# continuum/orchestrator/fusion_pipeline.py
# Modernized Fusion pipeline (Router-aware)

from continuum.core.logger import log_debug, log_error


class FusionPipeline:
    """
    Modernized Fusion pipeline.
    Router-aware, model-agnostic, and simplified.

    Responsibilities:
      - Adjust fusion weights
      - Run fusion engine
      - Pass routing metadata through
    """

    def __init__(self, controller, fusion_engine, fusion_filters):
        self.controller = controller
        self.fusion_engine = fusion_engine
        self.fusion_filters = fusion_filters

    # ---------------------------------------------------------
    # Adjust fusion weights
    # ---------------------------------------------------------
    def adjust(self, final_proposal):
        """
        Adjust fusion weights based on the final proposal.
        Router-aware: routing metadata is available if needed.
        """
        routing = self.controller.last_routing_decision

        log_debug(
            f"[FUSION] Adjusting fusion weights (intent={routing.get('intent') if routing else None})",
            phase="fusion"
        )

        # Existing logic unchanged
        return self.fusion_filters.adjust(final_proposal)

    # ---------------------------------------------------------
    # Run fusion
    # ---------------------------------------------------------
    def run(self, fusion_weights, ranked_proposals, controller, routing=None):
        """
        Execute the fusion engine.

        Router-aware:
          - routing metadata is passed into the fusion engine
          - fusion can use model/node info if needed
        """

        routing = routing or controller.last_routing_decision

        log_error("🔥 FUSION ENGINE RUN (Router-aware) 🔥", phase="fusion")

        fused = self.fusion_engine.run(
            fusion_weights=fusion_weights,
            ranked_proposals=ranked_proposals,
            controller=controller,
            routing=routing,   # ⭐ NEW: routing passed into fusion engine
        )

        log_debug(f"[FUSION] Fused output: {fused}", phase="fusion")

        return fused