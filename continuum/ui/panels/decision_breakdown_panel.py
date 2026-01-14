# continuum/ui/panels/decision_breakdown_panel.py

import streamlit as st
import pandas as pd

def render_decision_breakdown(controller):
    final = controller.last_final_proposal

    if not final:
        st.info("No decisions yet.")
        return

    st.title("Decision Breakdown")
    st.caption("Visual breakdown of Senate scores, Jury scores, and emotional alignment.")

    # ---------------------------------------------------------
    # 1. Show the user message
    # ---------------------------------------------------------
    st.subheader("User Message")
    st.info(controller.context.messages[-2].content)

    # ---------------------------------------------------------
    # 2. Show the winning actor
    # ---------------------------------------------------------
    st.subheader("Winning Actor")
    st.success(final["actor"])

    # ---------------------------------------------------------
    # 3. Build the chart data
    # ---------------------------------------------------------
    jury_scores = final["metadata"]["jury_scores"]

    df = pd.DataFrame({
        "Metric": [
            "Relevance",
            "Coherence",
            "Reasoning Quality",
            "Intent Alignment",
            "Emotional Alignment",
            "Novelty",
            "Memory Alignment"
        ],
        "Score": [
            jury_scores["relevance"],
            jury_scores["coherence"],
            jury_scores["reasoning_quality"],
            jury_scores["intent_alignment"],
            jury_scores["emotional_alignment"],
            jury_scores["novelty"],
            jury_scores["memory_alignment"]
        ]
    })

    # ---------------------------------------------------------
    # 4. Render the chart
    # ---------------------------------------------------------
    st.subheader("Jury Scoring Breakdown")
    st.bar_chart(df.set_index("Metric"))

    # ---------------------------------------------------------
    # 5. Jury reasoning
    # ---------------------------------------------------------
    st.subheader("Jury Reasoning")
    st.write(final["metadata"]["jury_reasoning"])

    # ---------------------------------------------------------
    # 6. Dissent
    # ---------------------------------------------------------
    st.subheader("Jury Dissent")
    st.info(final["metadata"]["jury_dissent"])