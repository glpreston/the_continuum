def apply_legacy_defaults(controller):
    """
    Provides Phase‑3 UI compatibility fields so the Streamlit app
    can run without modifying the new Phase‑4 controller architecture.
    """

    # Theme panel
    controller.theme_settings = {
        "mode": "Continuum",
        "font_size": "medium",
        "density": "comfortable",
        "accent_color": "blue",   # must match UI list
    }

    # Persona controls panel
    controller.narrator_mode = False

    # Tools panel
    controller.tool_logs = []

    # Reasoning panel (Senate/Jury ranked proposals)
    controller.last_ranked_proposals = []

    # Turn timeline panel
    controller.turn_history = []

    # Fusion debug output
    controller.last_raw_actor_output = ""

    # Meta‑Persona expects this to exist even before first turn
    controller.last_final_proposal = None