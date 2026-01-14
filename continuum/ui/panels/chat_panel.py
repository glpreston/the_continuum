# continuum/ui/panels/chat_panel.py

import streamlit as st

def render_chat(controller):
    st.subheader("Chat")

    user_input = st.chat_input("Say something to The Continuum...")

    if user_input:
        controller.context.add_user_message(user_input)
        controller.process_message(user_input)
        st.rerun()
  
    for m in controller.context.messages:
        st.write(f"{m.role}: {m.content[:80]}")

    for i, msg in enumerate(controller.context.messages):
        with st.chat_message(msg.role):
            st.write(msg.content)

            # -------------------------------------------------
            # RAW ACTOR OUTPUT TOGGLE (NEW)
            # -------------------------------------------------
            if msg.role == "assistant":
                if st.checkbox("Show raw actor output", key=f"raw_{i}"):
                    if hasattr(controller, "last_final_proposal"):
                        raw = controller.last_final_proposal.get("content", "")
                        st.markdown("**Raw Actor Output:**")
                        st.code(raw, language="markdown")
                    else:
                        st.info("No raw actor output available for this turn.")

            # -------------------------------------------------
            # META‑PERSONA SPEECH (your existing block)
            # -------------------------------------------------
            if msg.role == "assistant":
                from continuum.audio.meta_speech import speak_final_answer

                with st.container():
                    if st.checkbox("Speak this response", key=f"speak_{i}"):

                        # 1. Get full emotional synthesis result
                        result = speak_final_answer(controller, msg.content)

                        # 2. Extract audio
                        wav = result["audio"]

                        # 3. Play audio
                        import io, soundfile as sf
                        buffer = io.BytesIO()
                        sf.write(buffer, wav, 22050, format="WAV")
                        st.audio(buffer.getvalue(), format="audio/wav")

                        # 4. Emotional diagnostics panel
                        with st.expander("Meta‑Persona Emotional Diagnostics"):
                            st.write(f"**Topic:** {result['topic']}")
                            st.write(f"**Sentiment Polarity:** {result['sentiment_polarity']:.3f}")
                            st.write(f"**Sentiment Band:** {result['sentiment_band']}")

                            st.write("**Emotion Scores:**")
                            st.json(result["emotions"])

                            st.write("**Final Voice Modifiers:**")
                            st.json(result["final_modifiers"])