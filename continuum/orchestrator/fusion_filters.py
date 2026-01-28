# continuum/orchestrator/fusion_filters.py
# Modernized Fusion Filters (Router-aware, model-agnostic)

from continuum.core.logger import log_debug


class FusionFilters:
    """
    Phase‑5 Fusion Filters.

    Responsibilities:
      - Compute fusion weights for each actor
      - Remain model-agnostic (Router decides model/node)
      - Accept routing metadata for future adaptive weighting
    """

    def __init__(self, controller):
        self.controller = controller

    # ---------------------------------------------------------
    # Main weight adjustment entry point
    # ---------------------------------------------------------
    def adjust(self, final_proposal):
        """
        Compute fusion weights.

        Args:
            final_proposal: the Jury's chosen proposal
            (contains actor, content, metadata)

        Returns:
            dict: actor_name → weight
        """

        routing = self.controller.last_routing_decision

        log_debug(
            f"[FUSION FILTERS] Adjusting weights (intent={routing.get('intent') if routing else None})",
            phase="fusion"
        )

        # ---------------------------------------------------------
        # Phase‑4 behavior preserved:
        #   - All actors get equal weight unless overridden
        # ---------------------------------------------------------
        actor = final_proposal.get("actor", "Unknown")

        weights = {
            "Architect": 1.0,
            "Analyst": 1.0,
            "Storyweaver": 1.0,
            "Synthesizer": 1.0,
        }

        # ---------------------------------------------------------
        # Phase‑5 extension point:
        #   - Intent-aware weighting
        #   - Model-aware weighting
        #   - Actor bias from DB
        # ---------------------------------------------------------
        if routing:
            intent = routing.get("intent")
            model_choice = routing.get("model_selection", {})
            node_choice = routing.get("node_selection", {})

            # Example: if intent is "analysis", boost Analyst
            if intent == "analysis":
                weights["Analyst"] += 0.5

            # Example: if intent is "story", boost Storyweaver
            if intent == "story":
                weights["Storyweaver"] += 0.5

            # Example: if Synthesizer is the top model's preferred actor
            top_model = None
            if model_choice.get("candidates"):
                top_model = model_choice["candidates"][0]["model"]

            if top_model and "synth" in top_model.lower():
                weights["Synthesizer"] += 0.25

        # ---------------------------------------------------------
        # Normalize weights
        # ---------------------------------------------------------
        total = sum(weights.values())
        if total > 0:
            for k in weights:
                weights[k] /= total

        log_debug(f"[FUSION FILTERS] Final weights: {weights}", phase="fusion")
        return weights