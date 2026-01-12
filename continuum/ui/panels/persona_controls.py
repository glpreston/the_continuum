# continuum/ui/panels/persona_controls.py

import streamlit as st
from continuum.persona.meta_persona_profile import PERSONALITY_PRESETS, DEFAULT_PERSONALITY

def render_persona_controls(controller):
    st.subheader("Persona Voice")

    # Build a list of labels for the dropdown
    preset_labels = {key: data["label"] for key, data in PERSONALITY_PRESETS.items()}

    # Default selection
    current = st.session_state.get("meta_persona_preset", DEFAULT_PERSONALITY)

    # Dropdown selector
    choice = st.selectbox(
        "Select Meta‑Persona Personality",
        options=list(preset_labels.keys()),
        format_func=lambda key: preset_labels[key],
        index=list(preset_labels.keys()).index(current),
        key="meta_persona_selector", 
    )

    # Store selection in session state
    st.session_state.meta_persona_preset = choice
    controller.narrator_mode = st.checkbox("Narrator Mode", value=controller.narrator_mode)
    # Expose to controller (optional)
    controller.active_personality = choice

    st.caption(f"Active personality: **{preset_labels[choice]}**")