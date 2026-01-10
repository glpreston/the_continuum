# continuum/ui/panels/reasoning_panel.py

import streamlit as st

def render_reasoning(controller):
    st.header("Actor Reasoning")

    proposals = controller.last_ranked_proposals

    if not proposals:
        st.write("No proposals yet.")
        return

    for idx, p in enumerate(proposals, start=1):
        actor = p.get("actor", "unknown")
        content = p.get("content", "(no content)")
        confidence = p.get("confidence", 0.0)
        metadata = p.get("metadata", {})

        # Color-coded dot
        color_dot = (
            "🟢" if confidence > 0.7
            else "🟠" if confidence > 0.3
            else "🔴"
        )

        # Markdown-safe expander title
        title_md = f"{color_dot} **{idx}. {actor} — `{confidence:.2f}`**"

        # Single expander (correct)
        with st.expander(title_md, expanded=False):

            st.markdown("**Content:**")
            st.markdown(content)

            st.markdown(f"**Confidence:** `{confidence}`")

            if metadata:
                st.markdown("**Metadata:**")
                st.json(metadata)

            summary = p.get("summary", "No summary available.")
            st.markdown("**Reasoning Summary:**")
            st.markdown(summary)