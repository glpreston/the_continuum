import streamlit as st
from graphviz import Digraph

def render_flow(controller):
    st.header("Continuum Flow Diagram")

    ranked = controller.last_ranked_proposals
    final = controller.last_final_proposal
    raw = controller.context.debug_flags.get("raw_proposals", [])
    filtered = controller.context.debug_flags.get("filtered_proposals", [])

    # If nothing has happened yet
    if not ranked:
        st.write("No deliberation yet.")
        return

    dot = Digraph()

    # Style
    dot.attr(rankdir="TB", size="6,6")
    dot.attr("node", shape="box", style="rounded,filled", color="#444444", fillcolor="#eeeeee")

    # Nodes
    dot.node("actors", f"Actors\n({len(controller.actors)})")
    dot.node("raw", f"Raw Proposals\n({len(raw)})")
    dot.node("filtered", f"Filtered Proposals\n({len(filtered)})")
    dot.node("ranked", f"Ranked Proposals\n({len(ranked)})")

    winner = final.get("actor", "unknown") if final else "None"
    dot.node("jury", f"Jury Winner\n{winner}")

    # Edges
    dot.edge("actors", "raw")
    dot.edge("raw", "filtered")
    dot.edge("filtered", "ranked")
    dot.edge("ranked", "jury")

    st.graphviz_chart(dot)