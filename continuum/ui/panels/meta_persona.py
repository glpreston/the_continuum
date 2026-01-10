# continuum/ui/panels/meta_persona.py

import streamlit as st
import io
import soundfile as sf

from continuum.persona.voice_emotion import ACTOR_EMOTION
from continuum.audio.meta_speech import synthesize_meta_voice
from continuum.persona.meta_voice import blend_emotion
from continuum.audio.tts_engine import tts_engine

def render_meta_persona_panel(controller):
    st.subheader("Meta‑Persona Voice")

    # Text input for long-form synthesis
    long_text = st.text_area(
        "Text to speak as Meta‑Persona:",
        height=200,
        placeholder="Enter any text here…"
    )

    if st.button("Speak as Meta‑Persona"):
        if not long_text.strip():
            st.warning("Please enter some text.")
            return

        # Get Senate weights
        weights = {
            p["actor"]: p["confidence"]
            for p in controller.last_ranked_proposals
        }

        # Generate audio
        wav = synthesize_meta_voice(long_text, weights)

        buffer = io.BytesIO()
        sf.write(buffer, wav, 22050, format="WAV")
        st.audio(buffer.getvalue(), format="audio/wav")
