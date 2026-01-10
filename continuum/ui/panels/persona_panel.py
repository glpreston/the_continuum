import streamlit as st

def render_persona_controls(controller):
    st.header("Persona Controls")

    voice = st.selectbox(
        "Persona Voice",
        [
            "Warm, precise, collaborative",
            "Playful, metaphorical, curious",
            "Direct, analytical, minimal",
            "Poetic, expressive, lyrical",
        ],
        index=0,
    )
    controller.persona_settings["voice"] = voice

    st.subheader("Debug Options")
    show_meta = st.checkbox("Show meta-persona prefix", value=False)
    controller.persona_settings["show_meta_persona"] = show_meta

    show_actor = st.checkbox("Show winning actor name", value=False)
    controller.persona_settings["show_actor_name"] = show_actor