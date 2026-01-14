# continuum/ui/panels/decision_matrix_panel.py

import streamlit as st
import pandas as pd

def render_decision_matrix(controller):
    final = controller.last_final_proposal
    if not final or "metadata" not in final:
        st.info("No decision data available.")
        return

    # ---------------------------------------------------------
    # Extract metadata safely
    # ---------------------------------------------------------
    meta = final.get("metadata", {})
    all_scores = meta.get("jury_all_scores", {})
    winner = final.get("actor", "unknown")

    st.title("Decision Matrix")
    st.caption("Compare all actors across Jury scoring dimensions.")

    if not all_scores:
        st.info("No jury scores available.")
        return

    # ---------------------------------------------------------
    # Build the main matrix table
    # ---------------------------------------------------------
    rows = []
    for actor, scores in all_scores.items():
        rows.append({
            "Actor": actor,
            "Relevance": round(scores["relevance"], 3),
            "Coherence": round(scores["coherence"], 3),
            "Reasoning": round(scores["reasoning_quality"], 3),
            "Intent": round(scores["intent_alignment"], 3),
            "Emotion": round(scores["emotional_alignment"], 3),
            "Novelty": round(scores["novelty"], 3),
            "Memory": round(scores["memory_alignment"], 3),
            "Total": round(scores["total"], 3),
            "🏆": "✅" if actor == winner else ""
        })

    df = pd.DataFrame(rows)
    st.dataframe(df.style.highlight_max(axis=0, subset=["Total"], color="#d4f4dd"))

    # ---------------------------------------------------------
    # Jury reasoning
    # ---------------------------------------------------------
    st.subheader("Jury Reasoning")
    st.write(meta.get("jury_reasoning", "—"))

    # ---------------------------------------------------------
    # Jury dissent
    # ---------------------------------------------------------
    st.subheader("Jury Dissent")
    st.info(meta.get("jury_dissent", "—"))

    # ---------------------------------------------------------
    # Why Not the Runner-Up?
    # ---------------------------------------------------------
    st.subheader("Why Not the Runner-Up?")

    # Sort actors by total score
    sorted_actors = sorted(
        all_scores.items(),
        key=lambda x: x[1]["total"],
        reverse=True
    )

    if len(sorted_actors) > 1:
        runner_up, runner_up_scores = sorted_actors[1]

        st.write(f"**Runner-Up:** `{runner_up}`")

        # Compare winner vs runner-up dimension by dimension
        winner_scores = all_scores[winner]

        comparison_rows = []
        for metric in ["relevance", "coherence", "reasoning_quality",
                       "intent_alignment", "emotional_alignment",
                       "novelty", "memory_alignment", "total"]:
            comparison_rows.append({
                "Metric": metric,
                "Winner": round(winner_scores[metric], 3),
                "Runner-Up": round(runner_up_scores[metric], 3),
                "Difference": round(winner_scores[metric] - runner_up_scores[metric], 3)
            })

        comp_df = pd.DataFrame(comparison_rows)
        st.dataframe(comp_df)

        st.info(
            "This table shows exactly where the winner outperformed the runner-up. "
            "Positive differences indicate dimensions where the winner scored higher."
        )
    else:
        st.write("Not enough actors to compute a runner-up comparison.")

    # ---------------------------------------------------------
    # Actor Reasoning (per‑actor)
    # ---------------------------------------------------------
    st.subheader("Actor Reasoning")


    reasoning_traces = meta.get("reasoning_traces", {})

    for actor in all_scores.keys():
        with st.expander(f"{actor} — reasoning steps"):
            actor_trace = reasoning_traces.get(actor)

            if actor_trace:
                st.write("**Reasoning Steps:**")
                for step in actor_trace:
                    st.write(f"- {step}")
            else:
                st.write("No reasoning trace available for this actor.")