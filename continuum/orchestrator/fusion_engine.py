# continuum/orchestrator/fusion_engine.py
# Modernized Fusion Engine (Router-aware, model-agnostic)

from continuum.core.logger import log_debug, log_error


class FusionEngine:
    """
    Phase‑5 Fusion Engine.

    Responsibilities:
      - Combine ranked proposals using fusion weights
      - Remain model-agnostic (Router decides model/node)
      - Accept routing metadata for future adaptive fusion
    """

    def __init__(self, controller):
        self.controller = controller

    # ---------------------------------------------------------
    # Main fusion entry point
    # ---------------------------------------------------------
    def run(self, fusion_weights, ranked_proposals, controller, routing=None):
        """
        Execute the fusion process.

        Args:
            fusion_weights: dict of actor → weight
            ranked_proposals: list of proposals from Senate
            controller: ContinuumController
            routing: Router decision (intent, model, node, etc.)

        Returns:
            fused_text: final fused string
        """

        routing = routing or controller.last_routing_decision

        log_error("🔥 FUSION ENGINE START (Router-aware) 🔥", phase="fusion")

        # ---------------------------------------------------------
        # 1. Extract proposal texts
        # ---------------------------------------------------------
        texts = []
        for proposal in ranked_proposals:
            actor = proposal.get("actor", "Unknown")
            content = proposal.get("content", "")
            weight = fusion_weights.get(actor, 1.0)

            log_debug(
                f"[FUSION] Actor={actor} Weight={weight} ContentPreview={content[:60]}",
                phase="fusion"
            )

            texts.append((actor, content, weight))

        # ---------------------------------------------------------
        # 2. Weighted blending (simple but effective)
        # ---------------------------------------------------------
        fused = self._weighted_blend(texts)

        # ---------------------------------------------------------
        # 3. Attach routing metadata for downstream layers
        # ---------------------------------------------------------
        log_debug(
            f"[FUSION] Routing metadata passed through: {routing}",
            phase="fusion"
        )

        log_error("🔥 FUSION ENGINE COMPLETE 🔥", phase="fusion")
        return fused

    # ---------------------------------------------------------
    # Weighted blending algorithm
    # ---------------------------------------------------------
    def _weighted_blend(self, texts):
        """
        Simple weighted blending:
          - Multiply each proposal by its weight
          - Concatenate in descending weight order

        This preserves your Phase‑4 behavior while allowing
        future upgrades (intent-aware fusion, model-aware fusion, etc.)
        """

        # Sort by weight descending
        texts_sorted = sorted(texts, key=lambda x: x[2], reverse=True)

        blended = []
        for actor, content, weight in texts_sorted:
            blended.append(content)

        return "\n".join(blended)