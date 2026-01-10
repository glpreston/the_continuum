# continuum/ui/panels/chat_panel.py

import streamlit as st

def render_chat(controller):
    st.subheader("Chat")

    # Initialize flag
    if "pending_message" not in st.session_state:
        st.session_state.pending_message = None

    # Chat input
    user_input = st.chat_input("Say something to The Continuum...")

    # If user submitted a message
    if user_input:
        st.session_state.pending_message = user_input
        st.rerun()

    # If we have a pending message, process it now
    if st.session_state.pending_message:
        msg = st.session_state.pending_message

        # Add user message
        controller.context.add_user_message(msg)

        # Process through Senate → Jury → MetaPersona
        response = controller.process_message(msg)

        # Add assistant message
        controller.context.add_assistant_message(response)

        # Clear pending message
        st.session_state.pending_message = None

        # Rerun again to render updated history
        st.rerun()

    # ---------------------------------------------------------
    # Normal render: show full conversation history (ALWAYS)
    # ---------------------------------------------------------
    for i, msg in enumerate(controller.context.messages):
        with st.chat_message(msg.role):
            st.write(msg.content)

            # Only assistant messages get the speech option
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