import streamlit as st

def render_pipeline(controller):
    st.header("Senate Pipeline")

    ranked = controller.last_ranked_proposals
    final = controller.last_final_proposal
    raw = controller.context.debug_flags.get("raw_proposals", [])
    filtered = controller.context.debug_flags.get("filtered_proposals", [])

    # If nothing has happened yet
    if not ranked:
        st.write("No deliberation yet.")
        return

    # Summary row
    st.write("### Pipeline Summary")
    st.write(f"- **Actors:** {len(controller.actors)}")
    st.write(f"- **Raw Proposals:** {len(raw)}")
    st.write(f"- **Filtered Proposals:** {len(filtered)}")
    st.write(f"- **Ranked Proposals:** {len(ranked)}")
    st.write(f"- **Jury Winner:** {final.get('actor', 'unknown') if final else 'None'}")

    st.divider()

    # Visual pipeline
    st.write("### Flow")

    st.markdown("""
    <div style='font-size: 18px;'>
        🧠 <b>Actors</b>  
        &nbsp;&nbsp;&nbsp;⬇️  
        📝 <b>Proposals</b>  
        &nbsp;&nbsp;&nbsp;⬇️  
        🚫 <b>Filtered</b>  
        &nbsp;&nbsp;&nbsp;⬇️  
        📊 <b>Ranked</b>  
        &nbsp;&nbsp;&nbsp;⬇️  
        🏆 <b>Jury Winner</b>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Show raw proposals
    st.write("### Raw Proposals")
    for p in raw:
        st.json(p)

    st.divider()

    # Show filtered proposals
    st.write("### Filtered Proposals")
    for p in filtered:
        st.json(p)

import streamlit as st

def render_pipeline(controller):
    st.header("Senate Pipeline")

    ranked = controller.last_ranked_proposals or []
    if not ranked:
        st.write("No deliberation yet.")
        return

    st.subheader("Ranked Proposals")
    for p in ranked:
        with st.expander(f"{p.get('actor', 'Unknown')} — {p.get('confidence', 0):.2f}"):
            st.write("**Content:**", p.get("content"))
            st.write("**Metadata:**", p.get("metadata", {}))

    # --- Debug block (you can remove later) ---
    st.divider()
    st.subheader("Debug — Last Final Proposal")
    st.json(controller.last_final_proposal)

    st.subheader("Debug — Registered Actors")
    st.write(list(controller.actors.keys()))