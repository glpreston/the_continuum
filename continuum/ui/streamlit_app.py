# continuum/ui/streamlit_app.py

import streamlit as st
from continuum.orchestrator.continuum_controller import ContinuumController

# Panels
from continuum.ui.panels.chat_panel import render_chat
from continuum.ui.panels.actor_panel import render_actor_panel
from continuum.ui.panels.memory_panel import render_memory
from continuum.ui.panels.tools_panel import render_tools
from continuum.ui.panels.persona_controls import render_persona_controls
from continuum.ui.panels.reasoning_panel import render_reasoning
from continuum.ui.panels.pipeline_panel import render_pipeline
from continuum.ui.panels.flow_panel import render_flow
from continuum.ui.panels.actor_profiles_panel import render_actor_profiles
from continuum.ui.panels.actor_voiceprints_panel import render_actor_voiceprints
from continuum.ui.panels.meta_persona import render_meta_persona_panel
from continuum.ui.panels.emotional_memory_panel import render_emotional_memory
from continuum.ui.panels.senate_debate_panel import render_senate_debate
from continuum.ui.panels.traces_panel import render_traces
from continuum.ui.panels.theme_panel import render_theme_controls
from continuum.ui.panels.diagnostics_panel import render_diagnostics  # optional, if you still use it
from continuum.ui.panels.turn_timeline_panel import render_turn_timeline
from continuum.ui.panels.decision_breakdown_panel import render_decision_breakdown
from continuum.ui.panels.decision_matrix_panel import render_decision_matrix


# ---------------------------------------------------------
# Controller Builder
# ---------------------------------------------------------
def build_controller():
    return ContinuumController()


# ---------------------------------------------------------
# Main App
# ---------------------------------------------------------
def main():
    st.set_page_config(
        page_title="The Continuum",
        page_icon="∞",
        layout="wide",
    )

    # Session state initialization
    if "controller" not in st.session_state:
        st.session_state.controller = build_controller()

    controller = st.session_state.controller

    apply_theme(controller)

    # Title
    st.title("The Continuum")
    st.caption("Unified meta‑presence orchestrating internal actors")

    # ---------------------------------------------------------
    # SIDEBAR — Control Surface Only
    # ---------------------------------------------------------
    with st.sidebar:
        st.header("Controls")

        # Persona & Voice Controls
        st.subheader("Persona & Voice")
        controller.actor_voice_mode = st.checkbox(
            "Hear Actor Voices",
            value=getattr(controller, "actor_voice_mode", False),
            help="Enable to hear actors speak their lines aloud using text-to-speech.",
        )
        render_persona_controls(controller)

        # Senate Actors
        st.subheader("Senate Actors")
        render_actor_panel(controller)

        # Memory Controls
        st.subheader("Memory")
        render_memory(controller)

        # Clear Conversation Button
        if st.button("Clear Conversation"):
            controller.context.messages = []
            controller.emotional_memory.reset()
            st.rerun()

        # Theme & Layout
        st.subheader("Theme & Layout")
        render_theme_controls(controller)

        # Tools Panel
        st.subheader("Tools")
        render_tools(controller)

    # ---------------------------------------------------------
    # MAIN AREA — Chat + Diagnostics Tabs
    # ---------------------------------------------------------
    tabs = st.tabs(["Chat", "Diagnostics", "Decision Matrix"])

    # Chat Tab
    with tabs[0]:
        render_chat(controller)

    # Diagnostics Tab — Observability Surface
    with tabs[1]:
        st.title("Diagnostics")
        st.caption("Deep observability into The Continuum’s internal reasoning, emotions, and decision flow.")

        # 1. Emotional Diagnostics
        st.header("Emotional Diagnostics")
        st.write("Smoothed emotions, sentiment, and emotional memory over time.")
        render_emotional_memory(controller)
        st.markdown("---")

        # 2. Senate Diagnostics
        st.header("Senate Diagnostics")
        st.write("Actor proposals, rankings, and reasoning traces.")
        render_senate_debate(controller)    # Actor-level reasoning (voices optional)
        render_reasoning(controller)        # Ranked proposals + actor reasoning
        render_pipeline(controller)         # Raw → filtered → ranked → winner
        st.markdown("---")

        # 3. Jury Diagnostics
        st.header("Jury Diagnostics")
        st.write("Jury scoring, reasoning, and dissent notes.")
        # TODO: implement render_jury_diagnostics(controller) in a panel module
        # render_jury_diagnostics(controller)
        st.info("Jury diagnostics panel not yet implemented.")
        st.markdown("---")

        # 4. Turn Timeline (NEW)
        st.header("Turn Timeline")
        st.write("Chronological record of each turn: emotion → actor → jury → meta-persona → final output.")
        render_turn_timeline(controller)
        st.markdown("---")

        # 5. Continuum Traces
        st.header("Continuum Traces")
        st.write("Low-level event logs and internal pipeline traces.")
        render_traces(controller)
        st.markdown("---")

        # 6. Flow Diagram
        st.header("Continuum Flow Diagram")
        st.write("Visual representation of the full cognitive pipeline.")
        render_flow(controller)

    with tabs[2]:
        #render_decision_breakdown(controller)
        render_decision_matrix(controller)

# ---------------------------------------------------------
# Theme Application
# ---------------------------------------------------------
def apply_theme(controller):
    theme = controller.theme_settings
    css = ""

    # Font size
    if theme["font_size"] == "small":
        css += "html, body, [class*='css'] { font-size: 14px; }"
    elif theme["font_size"] == "large":
        css += "html, body, [class*='css'] { font-size: 20px; }"

    # Density
    if theme["density"] == "compact":
        css += ".block-container { padding-top: 1rem; padding-bottom: 1rem; }"
    elif theme["density"] == "spacious":
        css += ".block-container { padding-top: 4rem; padding-bottom: 4rem; }"

    # Accent color
    css += f"""
    :root {{
        --accent-color: {theme['accent_color']};
    }}
    .stButton>button {{
        background-color: var(--accent-color);
        color: white;
    }}
    """

    # Continuum theme mode
    if theme["mode"] == "Continuum":
        css += """
        body {
            background: linear-gradient(180deg, #0f0f1f, #1a1a2e);
            color: #e0e0ff;
        }
        """

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------
if __name__ == "__main__":
    main()