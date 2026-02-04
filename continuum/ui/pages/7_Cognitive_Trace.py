# continuum/ui/pages/7_Cognitive_Trace.py
import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import text

from continuum.orchestrator.continuum_controller import ContinuumController

#@st.cache_resource
#def get_controller():
#    return ContinuumController()

if "controller" not in st.session_state:
    st.session_state.controller = ContinuumController()

controller = st.session_state.controller


def main():
    st.set_page_config(page_title="Cognitive Trace", layout="wide")

    # Use the shared controller from session_state
    #if "controller" not in st.session_state:
    #    st.session_state.controller = ContinuumController()

    #controller = st.session_state.controller


    st.title("🧠 Cognitive Trace — How Aira Thinks")

    trace = getattr(controller, "last_trace", None)
    if not trace:
        st.info("No cognitive trace available yet. Ask Aira something on the main page first.")
        return

    timings = trace.get("timings", {})
    routing = trace.get("routing", {})
    ranked = trace.get("ranked_proposals", [])
    final_proposal = trace.get("final_proposal", {})
    fusion_output = trace.get("fusion_output", "")
    rewritten_output = trace.get("rewritten_output", "")
    actor_timings = trace.get("actor_timings", [])

    # ---------------------------------------------------------
    # 1. Timing Overview
    # ---------------------------------------------------------
    st.subheader("⏱️ Timing Breakdown")

    timing_rows = [
        {"Stage": "Emotion Detection", "Time (s)": timings.get("emotion_time")},
        {"Stage": "Deliberation (Senate + Jury)", "Time (s)": timings.get("deliberation_time")},
        {"Stage": "Fusion Adjust", "Time (s)": timings.get("fusion_adjust_time")},
        {"Stage": "Fusion Run", "Time (s)": timings.get("fusion_run_time")},
        {"Stage": "Rewrite", "Time (s)": timings.get("rewrite_time")},
        {"Stage": "Total", "Time (s)": timings.get("total_time")},
    ]
    st.dataframe(pd.DataFrame(timing_rows), width="stretch")

    # ---------------------------------------------------------
    # 2. Routing Info
    # ---------------------------------------------------------
    st.subheader("🛰️ Routing Decision")
    st.json(routing)

    # ---------------------------------------------------------
    # 3. Actor Performance (NEW)
    # ---------------------------------------------------------
    st.subheader("🎭 Actor Performance")

    if actor_timings:
        df_actor = pd.DataFrame(actor_timings)
        df_actor = df_actor[["actor", "model", "node", "duration", "tokens", "error"]]
        df_actor.rename(columns={
            "actor": "Actor",
            "model": "Model",
            "node": "Node",
            "duration": "Time (s)",
            "tokens": "Tokens",
            "error": "Error"
        }, inplace=True)


        st.dataframe(df_actor, width="stretch")

        st.markdown("### 🌐 Routing Overview")

        df_routing = df_actor[["Actor", "Model", "Node"]]
        st.dataframe(df_routing, width="stretch")


        st.markdown("#### 📚 Model Usage")

        model_chart = (
            alt.Chart(df_actor)
            .mark_bar()
            .encode(
                x=alt.X("Model:N", title="Model"),
                y=alt.Y("count()", title="Actors Using Model"),
                color="Model:N",
                tooltip=["Model", "count()"]
            )
            .properties(height=250)
        )

        st.altair_chart(model_chart, width="stretch")

        st.markdown("#### 🖥️ Node Usage")

        node_chart = (
            alt.Chart(df_actor)
            .mark_bar()
            .encode(
                x=alt.X("Node:N", title="Node"),
                y=alt.Y("count()", title="Actors Using Node"),
                color="Node:N",
                tooltip=["Node", "count()"]
            )
            .properties(height=250)
        )

        st.altair_chart(node_chart, width="stretch")

        st.markdown("#### 🔥 Actor × Node Heatmap")

        heatmap = (
            alt.Chart(df_actor)
            .mark_rect()
            .encode(
                x=alt.X("Node:N", title="Node"),
                y=alt.Y("Actor:N", title="Actor"),
                color=alt.Color("Time (s):Q", scale=alt.Scale(scheme="reds")),
                tooltip=["Actor", "Node", "Time (s)", "Tokens"]
            )
            .properties(height=200)
        )

        st.altair_chart(heatmap, width="stretch")

        st.markdown("#### 🔧 Actor × Model Heatmap")

        heatmap2 = (
            alt.Chart(df_actor)
            .mark_rect()
            .encode(
                x=alt.X("Model:N", title="Model"),
                y=alt.Y("Actor:N", title="Actor"),
                color=alt.Color("Time (s):Q", scale=alt.Scale(scheme="blues")),
                tooltip=["Actor", "Model", "Time (s)", "Tokens"]
            )
            .properties(height=200)
        )

        st.altair_chart(heatmap2, width="stretch")

        # Deliberation timing chart
        st.markdown("#### ⏱️ Deliberation Time by Actor")

        chart = (
            alt.Chart(df_actor)
            .mark_bar()
            .encode(
                x=alt.X("Actor:N", sort="-y", title="Actor"),
                y=alt.Y("Time (s):Q", title="Duration (seconds)"),
                color=alt.Color("Actor:N", legend=None),
                tooltip=["Actor", "Time (s)", "Tokens", "Error"],
            )
            .properties(height=300)
        )
        st.altair_chart(chart, width="stretch")
    else:
        st.write("No actor timing data available.")

    # ---------------------------------------------------------
    # 4. Actor / Senate Proposals
    # ---------------------------------------------------------
    st.subheader("📝 Actor / Senate Proposals")

    if not ranked:
        st.write("No ranked proposals available.")
    else:
        for i, proposal in enumerate(ranked, start=1):
            actor_name = proposal.get("actor", f"Actor {i}")
            title = f"{i}. {actor_name}"
            with st.expander(title):
                st.write(proposal.get("content", ""))
                if "confidence" in proposal:
                    st.caption(f"Confidence: {proposal.get('confidence')}")
                if "summary" in proposal:
                    st.markdown("**Summary:**")
                    st.write(proposal.get("summary"))
                if "metadata" in proposal and proposal["metadata"].get("type") == "error":
                    st.error(f"Actor Error: {proposal['metadata'].get('error')}")

    # ---------------------------------------------------------
    # 5. Jury Final Proposal
    # ---------------------------------------------------------
    st.subheader("⚖️ Jury Final Proposal")

    with st.expander("Final Proposal"):
        st.write(final_proposal.get("content", ""))
        st.caption(f"Actor: {final_proposal.get('actor')}")

    # ---------------------------------------------------------
    # 6. Fusion Output
    # ---------------------------------------------------------
    st.subheader("🔗 Fusion Output (Pre‑Rewrite)")

    with st.expander("Fusion Output"):
        st.write(fusion_output)

    # ---------------------------------------------------------
    # 7. Aira Rewrite
    # ---------------------------------------------------------
    st.subheader("✨ Aira Rewrite")

    with st.expander("Rewritten Output"):
        st.write(rewritten_output)

    # ---------------------------------------------------------
    # 8. Historical Cognitive Traces
    # ---------------------------------------------------------
    st.subheader("📜 Historical Cognitive Traces (Last 50)")

    rows = controller.db.execute(
        text("SELECT id, timestamp, actor_name, model_name, node_name, "
             "total_time, senate_time, fusion_time, rewrite_time, "
             "actor_confidence, actor_output_length, jury_winner, rewrite_delta "
             "FROM cognitive_trace ORDER BY id DESC LIMIT 50")
    ).mappings().all()

    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch")
    else:
        st.write("No cognitive trace records found in the database.")

if __name__ == "__main__":
    main()