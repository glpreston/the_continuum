# continuum/ui/panels/components/actor_fusion_trace.py

import streamlit as st
import pandas as pd


def render_actor_fusion_trace(controller):
    st.subheader("Actor Fusion Trace (Senate + Jury)")

    ranked = getattr(controller, "last_ranked_proposals", []) or []
    final = getattr(controller, "last_final_proposal", None)

    if not ranked and not final:
        st.info("No actor decisions available yet.")
        return

    if ranked:
        rows = []
        for idx, proposal in enumerate(ranked, start=1):
            rows.append(
                {
                    "Rank": idx,
                    "Actor": proposal.get("actor", "unknown"),
                    "Score": proposal.get("score", None),
                    "Reason": proposal.get("reason", ""),
                }
            )
        st.markdown("**Senate Ranked Proposals**")
        st.dataframe(pd.DataFrame(rows), width="stretch")

    if final:
        st.markdown("**Jury Final Decision**")
        st.json(final)