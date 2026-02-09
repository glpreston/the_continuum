# continuum/orchestrator/controller_legacy.py
# Legacy UI compatibility layer for the new modular ContinuumController.
# This file restores all fields the old Streamlit UI expects.

class LegacyUIFields:
    """
    Provides legacy attributes expected by the old Streamlit UI.
    This keeps the new modular ContinuumController clean while
    maintaining backward compatibility with the existing UI.
    """

    def _init_legacy_fields(self):
        # ---------------------------------------------------------
        # Theme panel compatibility
        # ---------------------------------------------------------
        self.theme_settings = {
            "mode": "Light",          # UI expects: "Light" / "Dark" / "Continuum"
            "accent_color": "blue",   # UI expects a named color
            "font_size": "medium",    # UI expects: "small" / "medium" / "large"
            "density": "comfortable", # UI expects: "compact" / "comfortable" / "spacious"
        }

        # ---------------------------------------------------------
        # Persona controls compatibility
        # ---------------------------------------------------------
        self.narrator_mode = False   # UI checkbox

        # ---------------------------------------------------------
        # Tools panel compatibility
        # ---------------------------------------------------------
        self.tool_logs = []          # UI displays tool call logs

        # ---------------------------------------------------------
        # Reasoning panel compatibility
        # ---------------------------------------------------------
        self.last_ranked_proposals = []  # Senate/Jury ranked proposals
        self.last_final_proposal = None  # Final fused output

        # ---------------------------------------------------------
        # Turn timeline compatibility
        # ---------------------------------------------------------
        self.turn_history = []       # UI expects a list of turn dicts