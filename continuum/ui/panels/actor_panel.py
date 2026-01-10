import streamlit as st
from continuum.persona.actor_cards import ACTOR_CARDS
from continuum.persona.voiceprints import VOICEPRINTS
from continuum.actors.utils import generate_voice_preview, generate_voice_audio
from continuum.audio.tts_engine import CoquiEngine
from continuum.persona.voice_speakers import ACTOR_SPEAKERS
from continuum.persona.voice_emotion import ACTOR_EMOTION



# Load once globally
tts_engine = CoquiEngine()


def render_actor_panel(controller):
    st.subheader("Senate Actors")

    for actor_name, actor in controller.actors.items():

        card = ACTOR_CARDS.get(actor_name)
        voice = VOICEPRINTS.get(actor_name)
        settings = controller.actor_settings.get(actor_name, {})

        with st.expander(f"{voice.ui['icon']}  {voice.ui['label']}", expanded=False):

            # -------------------------
            # Enable / Disable
            # -------------------------
            enabled = st.checkbox(
                "Enabled",
                value=settings.get("enabled", True),
                key=f"{actor_name}_enabled",
            )
            settings["enabled"] = enabled

            # -------------------------
            # Weight slider
            # -------------------------
            weight = st.slider(
                "Weight",
                min_value=0.0,
                max_value=3.0,
                value=settings.get("weight", 1.0),
                step=0.1,
                key=f"{actor_name}_weight",
            )
            settings["weight"] = weight

            # -------------------------
            # Actor Profile (J12)
            # -------------------------
            if card:
                st.markdown(f"**Role:** {card.role_name}")
                st.markdown(f"**Essence:** {card.essence}")

            # -------------------------
            # Voiceprint (J13)
            # -------------------------
            if voice:
                st.markdown(f"**Voice:** {voice.ui['label']}")
                st.caption(f"Tone: {voice.tone}")

            # -------------------------
            # Voice Preview (Text)
            # -------------------------
            if st.button("Preview Voice (Text)", key=f"{actor_name}_preview_text"):
                preview = generate_voice_preview(actor)
                st.markdown(f"**Preview:** {preview}")

            # -------------------------
            # Voice Preview (Audio)
            # -------------------------
            if st.button("Preview Voice (Audio)", key=f"{actor_name}_preview_audio"):
                preview_text = generate_voice_preview(actor)
                speaker = ACTOR_SPEAKERS.get(actor_name, tts_engine.speakers[0])
                emotion = ACTOR_EMOTION.get(actor_name, {})

                wav = tts_engine.synthesize(
                    preview_text,
                    speaker=speaker,
                    speed=emotion.get("speed", 1.0),
                    energy=emotion.get("energy", 1.0),
                    pitch=emotion.get("pitch", 1.0),
                )

                import soundfile as sf
                import io
                buffer = io.BytesIO()
                sf.write(buffer, wav, 22050, format="WAV")
                st.audio(buffer.getvalue(), format="audio/wav")

            # Save back to controller
            controller.actor_settings[actor_name] = settings