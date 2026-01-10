import streamlit as st
from continuum.orchestrator.continuum_controller import ContinuumController

# Import SpecialistActor    
from continuum.actors.specialist_actor import SpecialistActor

from continuum.ui.panels.traces_panel import render_traces
from continuum.ui.panels.memory_panel import render_memory
from continuum.ui.panels.tools_panel import render_tools
from continuum.ui.panels.persona_panel import render_persona_controls
from continuum.ui.panels.chat_panel import render_chat
from continuum.ui.panels.actor_panel import render_actor_panel
from continuum.ui.panels.theme_panel import render_theme_controls
from continuum.ui.panels.reasoning_panel import render_reasoning
from continuum.ui.panels.pipeline_panel import render_pipeline
from continuum.ui.panels.flow_panel import render_flow
from continuum.ui.panels.actor_profiles_panel import render_actor_profiles
from continuum.ui.panels.actor_voiceprints_panel import render_actor_voiceprints
from continuum.ui.panels.meta_persona import render_meta_persona_panel

def build_controller():
    return ContinuumController()


def main():
    st.set_page_config(
        page_title="The Continuum",
        page_icon="∞",
        layout="wide",
    )

    if "controller" not in st.session_state:
        st.session_state.controller = build_controller()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    controller = st.session_state.controller

    apply_theme(controller)

    # Title + UI (only once)
    st.title("The Continuum")
    st.caption("Unified meta‑presence orchestrating internal actors")

    with st.sidebar:
        render_traces(controller)
        render_memory(controller)
        render_tools(controller)
        render_persona_controls(controller)
        render_actor_panel(controller)
        render_theme_controls(controller)
        render_reasoning(controller)
        render_pipeline(controller)
        render_flow(controller)
        render_meta_persona_panel(controller)

    render_chat(controller)

    with st.sidebar:
        ...
        render_actor_profiles()        # J12
        render_actor_voiceprints()     # J13
        ...

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

if __name__ == "__main__":
    main()