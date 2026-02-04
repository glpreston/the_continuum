# continuum/ui/pages/2_Debug.py

import streamlit as st
import pandas as pd
from continuum.orchestrator.continuum_controller import ContinuumController


#@st.cache_resource
#def get_controller():
#    return ContinuumController()


#def main():
    #st.set_page_config(page_title="Debug", layout="wide")
    #controller = get_controller()

if "controller" not in st.session_state:
    st.session_state.controller = ContinuumController()

controller = st.session_state.controller    

def main():
    st.set_page_config(page_title="Cognitive Trace", layout="wide")

    st.title("🛠️ Debug — Actors, Jury, Fusion, Routing, Pipeline")

    # -------------------------------------------------------------------------
    # Guard: ensure debug data exists
    # -------------------------------------------------------------------------
    if not hasattr(controller, "turn_logger"):
        st.warning("Debug data not available yet.")
        return

    if len(controller.turn_logger) == 0:
        st.info("No debug data yet. Send a message through the chat first.")
        return

    # Always inspect the most recent turn
    last_turn = controller.turn_logger[-1]

    # -------------------------------------------------------------------------
    # 1. Actor Outputs
    # -------------------------------------------------------------------------
    st.subheader("🎭 Actor Outputs")

    actors = last_turn.get("actors", {})
    if not actors:
        st.info("No actor outputs recorded for this turn.")
    else:
        for actor_name, actor_data in actors.items():
            with st.expander(f"Actor: {actor_name}"):
                st.markdown("**Raw Output:**")
                st.write(actor_data.get("raw_output", ""))

                if "analysis" in actor_data:
                    st.markdown("**Analysis:**")
                    st.write(actor_data["analysis"])

                if "score" in actor_data:
                    st.markdown("**Score:**")
                    st.write(actor_data["score"])

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 2. Jury Scoring
    # -------------------------------------------------------------------------
    st.subheader("⚖️ Jury Scoring")

    jury_scores = last_turn.get("jury_scores", {})
    if not jury_scores:
        st.info("No jury scoring available.")
    else:
        df = pd.DataFrame(jury_scores).T
        st.dataframe(df, width=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 3. Fusion Trace
    # -------------------------------------------------------------------------
    st.subheader("🧬 Fusion Trace")

    fusion = last_turn.get("fusion", {})
    if not fusion:
        st.info("No fusion trace available.")
    else:
        with st.expander("Fusion Summary"):
            st.write(fusion.get("summary", ""))

        with st.expander("Sentence-Level Trace"):
            trace = fusion.get("trace", [])
            for step in trace:
                st.markdown(f"**{step.get('source', 'Unknown')}** → {step.get('text', '')}")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 4. Rewrite Trace (Meta-Persona)
    # -------------------------------------------------------------------------
    st.subheader("🌀 Meta‑Persona Rewrite Trace")

    rewrite = last_turn.get("rewrite_trace", {})
    if not rewrite:
        st.info("No rewrite trace available.")
    else:
        for depth, entry in rewrite.items():
            with st.expander(f"Rewrite Depth {depth}"):
                st.markdown("**Input:**")
                st.write(entry.get("input", ""))

                st.markdown("**Output:**")
                st.write(entry.get("output", ""))

                if "notes" in entry:
                    st.markdown("**Notes:**")
                    st.write(entry["notes"])

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 5. Pipeline Step Log
    # -------------------------------------------------------------------------
    st.subheader("🔧 Pipeline Step Log")

    pipeline_steps = last_turn.get("pipeline_steps", [])
    if not pipeline_steps:
        st.info("No pipeline steps recorded.")
    else:
        for step in pipeline_steps:
            with st.expander(step.get("name", "Unnamed Step")):
                st.write(step.get("data", ""))

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 6. Routing Decision Inspector
    # -------------------------------------------------------------------------
    st.subheader("🛰️ Routing Decision")

    routing = getattr(controller, "last_routing_decision", None)
    if routing:
        st.json(routing)
    else:
        st.info("No routing decision recorded yet.")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 7. Turn Log Viewer
    # -------------------------------------------------------------------------
    st.subheader("📜 Turn Log (All Turns)")

    for i, turn in enumerate(controller.turn_logger):
        with st.expander(f"Turn {i+1}"):
            st.json(turn)


if __name__ == "__main__":
    main()