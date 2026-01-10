# continuum/ui/panels/actor_voiceprints_panel.py

import streamlit as st
from continuum.persona.voiceprints import VOICEPRINTS, Voiceprint


def render_actor_voiceprints():
    """Render the J13 Actor Voiceprints in the sidebar."""

    st.subheader("Actor Voiceprints")

    for actor_id, vp in VOICEPRINTS.items():
        with st.expander(f"{vp.ui['icon']}  {vp.ui['label']} Voiceprint", expanded=False):

            # Tone
            st.markdown(f"**Tone:** {vp.tone}")

            # Rhythm
            st.markdown(f"**Rhythm:** {vp.rhythm}")

            # Sentence Shape
            st.markdown(f"**Sentence Shape:** {vp.sentence_shape}")

            # Lexical Palette
            st.markdown("**Lexical Palette**")
            st.markdown(", ".join(vp.lexical_palette))

            # Signature Moves
            st.markdown("**Signature Moves**")
            for move in vp.signature_moves:
                st.markdown(f"- {move}")

            # Example Output
            st.markdown("**Example Output (Style Only)**")
            st.markdown(f"> {vp.example_output}")

            # UI Metadata (optional)
            st.caption(f"Color: {vp.ui['color']} • Actor ID: {vp.actor_id}")