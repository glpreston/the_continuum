# continuum/ui/panels/actor_voiceprints_panel.py

import streamlit as st
import io
import soundfile as sf

from continuum.persona.voiceprints import VOICEPRINTS, Voiceprint
from continuum.persona.actor_voice_timbre import ACTOR_TIMBRE
from continuum.audio.tts_engine import tts_engine
from continuum.persona.actor_speakers import ACTOR_SPEAKERS


def wav_bytes_from_array(wav_array, sample_rate=22050):
    buffer = io.BytesIO()
    sf.write(buffer, wav_array, sample_rate, format="WAV")
    buffer.seek(0)
    return buffer.read()

def render_actor_voiceprints():
    """Render the J13 Actor Voiceprints in the sidebar."""
    st.subheader("Actor Voiceprints")

    for actor_id, vp in VOICEPRINTS.items():
        with st.expander(f"{vp.ui['icon']}  {vp.ui['label']} Voiceprint", expanded=False):

            # ---------------------------------------------------------
            # Cognitive Voiceprint (existing)
            # ---------------------------------------------------------

            st.markdown("### Cognitive Voiceprint")

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

            # UI Metadata
            st.caption(f"Color: {vp.ui['color']} • Actor ID: {vp.actor_id}")

            # ---------------------------------------------------------
            # Acoustic Timbre Profile (new)
            # ---------------------------------------------------------

            timbre = ACTOR_TIMBRE.get(actor_id)

            if timbre:
                st.markdown("---")
                st.markdown("### Acoustic Timbre Profile")

                st.write(f"**Vocal Weight:** {timbre.get('vocal_weight')}")
                st.write(f"**Brightness:** {timbre.get('brightness')}")
                st.write(f"**Resonance:** {timbre.get('resonance')}")
                st.write(f"**Clarity:** {timbre.get('clarity')}")

                st.markdown("**Expressive Traits**")
                st.write(f"- Texture: {timbre.get('texture')}")
                st.write(f"- Smoothness: {timbre.get('smoothness')}")

                st.markdown("**Emotional Range**")
                st.write(f"Range: {timbre.get('emotional_range')}")

                allowed = ", ".join(timbre.get("allowed_emotions", []))
                forbidden = ", ".join(timbre.get("forbidden_emotions", []))

                st.write(f"Allowed: {allowed}")
                st.write(f"Forbidden: {forbidden}")

            else:
                st.info("No acoustic timbre profile defined for this actor.")

            # ---------------------------------------------------------
            # Preview Voice button
            # ---------------------------------------------------------
            if st.button("🔊 Preview Voice", key=f"preview_{actor_id}"):
                sample_text = "This is how my voice sounds in The Continuum."

                # Get speaker + timbre for this actor
                speaker_info = ACTOR_SPEAKERS.get(actor_id, {})
                speaker_id = speaker_info.get("speaker_id", "p225")
                timbre = speaker_info.get("timbre")

                # Synthesize audio
                wav = tts_engine.synthesize(
                    sample_text,
                    speaker=speaker_id,
                    speed=1.0,
                    energy=1.0,
                    pitch=1.0,
                    timbre=timbre,
                )
                # Playback
                # Convert NumPy array → WAV bytes
                wav_bytes = wav_bytes_from_array(wav)

                # Playback
                st.audio(wav_bytes, format="audio/wav")