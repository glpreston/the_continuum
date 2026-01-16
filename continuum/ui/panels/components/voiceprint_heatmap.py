# continuum/ui/panels/components/voiceprint_heatmap.py

import streamlit as st
import pandas as pd


def render_voiceprint_heatmap(controller, emotional_state, style):
    st.subheader("Voiceprint Alignment Snapshot")

    if style is None:
        st.info("No style vector available.")
        return

    # Build table
    rows = []
    for key, value in style.items():
        delta = value - 1.0
        rows.append({
            "Dimension": key,
            "Style Value": round(value, 3),
            "Delta": round(delta, 3),
        })

    df = pd.DataFrame(rows)

    # Color rows based on Delta
    def color_row(row):
        delta = row["Delta"]
        if delta > 0.15:
            return ["background-color: #b6f2b6"] * len(row)   # greenish
        elif delta < -0.15:
            return ["background-color: #f2b6b6"] * len(row)   # reddish
        else:
            return ["background-color: #f2f2f2"] * len(row)   # neutral gray

    st.dataframe(
        df.style.apply(color_row, axis=1),
         width="stretch"
    )