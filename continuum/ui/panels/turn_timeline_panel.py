import streamlit as st

def render_turn_timeline(controller):
    turns = controller.turn_history

    if not turns:
        st.info("No turns recorded yet.")
        return

    for i, turn in enumerate(turns, start=1):
        st.markdown(f"### Turn {i}")
        st.markdown("---")

        # User message
        st.write("**User Message:**")
        st.info(turn["user"])

        # Emotion (safe display)
        st.write("**Detected Emotion:**")
        emotion = turn.get("emotion", {})
        if isinstance(emotion, dict):
            st.write(f"- Label: `{emotion.get('label', 'N/A')}`")
            st.write(f"- Intensity: `{emotion.get('intensity', 0):.3f}`")
        else:
            st.write(emotion)

        # Winning actor
        final = turn.get("final_proposal", {})
        actor = final.get("actor", "Unknown")
        st.write(f"**Winning Actor:** `{actor}`")

        # Jury score
        if "confidence" in final:
            st.write(f"**Jury Score:** {final['confidence']:.3f}")

        # Assistant response
        st.write("**Assistant Response:**")
        st.success(turn.get("assistant", ""))

        st.markdown("---")