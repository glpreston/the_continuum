# continuum/ui/panels/components/rewrite_diff_viewer.py

import streamlit as st
import difflib


def render_rewrite_diff_viewer(controller):
    st.subheader("Rewrite‑Stage Diff Viewer")

    raw = getattr(controller, "last_raw_actor_output", None)
    final = None
    if controller.context and controller.context.messages:
        # last assistant message is the Meta‑Persona rewrite
        for msg in reversed(controller.context.messages):
            if msg.role == "assistant":
                final = msg.content
                break

    if not raw or not final:
        st.info("No rewrite data available yet.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Actor Output**")
        st.text(raw)

    with col2:
        st.markdown("**Final Meta‑Persona Output**")
        st.text(final)

    st.markdown("**Diff (Actor → Meta‑Persona)**")
    diff = difflib.unified_diff(
        raw.splitlines(),
        final.splitlines(),
        lineterm="",
        fromfile="actor",
        tofile="meta_persona",
    )
    st.code("\n".join(diff) or "No differences.")
    