# continuum/ui/panels/emotional_memory_panel.py

import streamlit as st

def render_emotional_memory(controller):
    st.subheader("Emotional Memory")

    if not hasattr(controller, "emotional_memory"):
        st.info("Emotional memory not initialized.")
        return

    memory = controller.emotional_memory

    if memory.is_empty():
        st.caption("No emotional history yet.")
        return

    state = memory.get_smoothed_state()

    # Display averaged sentiment
    st.markdown("### Smoothed Sentiment")
    st.write(f"**Average Sentiment Polarity:** {state['avg_sentiment']:.3f}")

    # Display averaged emotions
    st.markdown("### Smoothed Emotions")
    st.json(state["avg_emotions"])

    # Optional: show raw events
    with st.expander("Raw Emotional Events (debug)"):
        st.write(list(memory.events))

    # Reset button
    if st.button("Reset Emotional Memory"):
        memory.events.clear()
        st.success("Emotional memory cleared.")
        st.rerun()