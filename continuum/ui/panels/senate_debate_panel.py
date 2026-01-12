# continuum/ui/panels/senate_debate_panel.py

import streamlit as st

def render_senate_debate(controller):
    st.subheader("Senate Debate (Voices)")

    proposals = getattr(controller, "last_ranked_proposals", None)
    if not proposals:
        st.info("No proposals yet. Send a message to the Continuum.")
        return

    for i, p in enumerate(proposals, start=1):
        actor = p.get("actor", "unknown")
        role = p.get("metadata", {}).get("role", "")
        content = p.get("content", "")
        audio = p.get("audio")

        with st.expander(f"{i}. {actor} — {role}"):
            st.markdown(f"**Text:** {content}")

            if audio is not None:
                st.audio(audio, format="audio/wav")
            else:
                st.caption("No audio generated for this proposal.")