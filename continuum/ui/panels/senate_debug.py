# continuum/ui/panels/senate_debug.py

import streamlit as st

def senate_debate_panel(controller):
    st.subheader("Senate Debate (Voices)")

    proposals = getattr(controller, "last_ranked_proposals", None)
    if not proposals:
        st.info("No proposals yet. Send a message to the Continuum.")
        return

    for i, p in enumerate(proposals, start=1):
        with st.expander(f"{i}. {p['actor']} — {p['metadata'].get('role', '')}"):
            st.markdown(f"**Text:** {p['content']}")
            audio = p.get("audio")
            if audio is not None:
                st.audio(audio, format="audio/wav")
            else:
                st.caption("No audio generated for this proposal.")