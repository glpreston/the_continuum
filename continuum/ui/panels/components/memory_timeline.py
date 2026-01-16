# continuum/ui/panels/components/memory_timeline.py

import streamlit as st
import pandas as pd


def render_memory_timeline(controller, emotional_memory):
    st.subheader("Emotional Memory Timeline")

    events = getattr(emotional_memory, "events", [])
    if not events:
        st.info("No emotional memory events recorded yet.")
        return

    rows = []
    for idx, ev in enumerate(events, start=1):
        raw = ev.raw_state if hasattr(ev, "raw_state") else ev.get("raw_state", {})
        dominant = getattr(ev, "dominant_emotion", None) or ev.get("dominant_emotion", "")
        rows.append(
            {
                "Step": idx,
                "Dominant Emotion": dominant,
                **raw,
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch")