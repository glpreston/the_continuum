# continuum/ui/panels/components/emotional_trend_charts.py

import streamlit as st
import pandas as pd


def render_emotional_trend_charts(controller, emotional_state, emotional_memory):
    st.subheader("Emotional Trends Over Time")

    events = getattr(emotional_memory, "events", [])
    if not events:
        st.info("No emotional events recorded yet.")
        return

    rows = []
    for idx, ev in enumerate(events, start=1):
        raw = ev.raw_state if hasattr(ev, "raw_state") else ev.get("raw_state", {})
        row = {"Step": idx}
        row.update(raw)
        rows.append(row)

    df = pd.DataFrame(rows).set_index("Step")
    st.line_chart(df)
    