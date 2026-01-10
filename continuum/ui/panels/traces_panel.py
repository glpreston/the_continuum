import streamlit as st

def render_traces(controller):
    st.header("Continuum Traces")

    # Senate Rankings
    st.subheader("Senate Rankings")
    if controller.last_ranked_proposals:
        for idx, proposal in enumerate(controller.last_ranked_proposals, start=1):
            st.markdown(f"**{idx}. {proposal.get('actor', 'unknown')}**")
            st.write(proposal.get("content", "(no content)"))
            st.caption(f"Score: {proposal.get('score', 'N/A')}")
            st.divider()
    else:
        st.write("No proposals yet.")

    # Jury Decision
    st.subheader("Jury Decision")
    if controller.last_final_proposal:
        st.markdown(f"**Winner: {controller.last_final_proposal.get('actor', 'unknown')}**")
        st.write(controller.last_final_proposal.get("content", "(no content)"))
    else:
        st.write("No decision yet.")