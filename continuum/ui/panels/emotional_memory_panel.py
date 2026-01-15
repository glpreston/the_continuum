# continuum/ui/panels/emotional_memory_panel.py
# version EI‑2.0

import streamlit as st

def render_emotional_memory(controller):
    st.subheader("Emotional Memory")

    if not hasattr(controller, "emotional_memory"):
        st.info("Emotional memory not initialized.")
        return

    memory = controller.emotional_memory

    if not memory.events:
        st.info("No emotional events recorded yet.")
        return

    state = memory.get_smoothed_state()

    dominant = state.get("dominant_emotion", "unknown")
    confidence = state.get("confidence", 0.0)
    volatility = state.get("volatility", 0.0)
    smoothed = state.get("smoothed_state", {})

    # EI‑2.0 summary
    st.markdown("### EI‑2.0 Emotional Summary")
    st.write(f"**Dominant Emotion:** {dominant}")
    st.write(f"**Confidence:** {confidence:.3f}")
    st.write(f"**Volatility:** {volatility:.3f}")

    # Smoothed vector
    st.markdown("### Smoothed Emotional State")
    st.json(smoothed)

    # Phase‑4 emotional state (if available)
    if hasattr(controller, "emotional_state") and controller.emotional_state:
        st.markdown("### Phase‑4 Emotional State (Debug)")
        st.json(controller.emotional_state.as_dict())

    # Raw events
    with st.expander("Raw Emotional Events (debug)"):
        st.json([e.__dict__ for e in memory.events])

    # Reset button
    if st.button("Reset Emotional Memory"):
        memory.events.clear()
        st.success("Emotional memory cleared.")
        st.rerun()