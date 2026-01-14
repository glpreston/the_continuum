import streamlit as st
import pandas as pd

def render_diagnostics(controller):
    st.header("Emotional Diagnostics")

    # Get emotional state (may be minimal)
    state = controller.emotional_memory.get_smoothed_state()

    # -------------------------
    # Summary Table (robust)
    # -------------------------
    st.subheader("Summary")

    summary_rows = []

    # Mode (fallback)
    summary_rows.append({
        "Metric": "Mode",
        "Value": state.get("mode", "N/A")
    })

    # Volatility (fallback)
    summary_rows.append({
        "Metric": "Volatility",
        "Value": state.get("volatility", "N/A")
    })

    # Confidence (fallback)
    summary_rows.append({
        "Metric": "Confidence",
        "Value": state.get("confidence", "N/A")
    })

    # Sentiment (your engine returns this)
    summary_rows.append({
        "Metric": "Avg Sentiment",
        "Value": state.get("avg_sentiment", "N/A")
    })

    summary_df = pd.DataFrame(summary_rows)
    summary_df["Value"] = summary_df["Value"].astype(str)
    st.table(summary_df)

    # -------------------------
    # Smoothed Emotions
    # -------------------------
    st.subheader("Smoothed Emotions")

    smoothed = state.get("smoothed") or state.get("avg_emotions") or {}

    if smoothed:
        smoothed_df = pd.DataFrame(
            [{"Emotion": k, "Intensity": round(v, 3)} for k, v in smoothed.items()]
        )
        st.table(smoothed_df)
    else:
        st.write("None")

    # -------------------------
    # Short-Term Snapshot
    # -------------------------
    st.subheader("Short-Term Snapshot")

    short_term = state.get("short_term") or {}
    if short_term:
        st.json(short_term)
    else:
        st.write("None")

    # -------------------------
    # Long-Term Snapshot
    # -------------------------
    st.subheader("Long-Term Snapshot")

    long_term = state.get("long_term") or {}
    if long_term:
        st.json(long_term)
    else:
        st.write("None")

    # -------------------------
    # Raw Emotional Events
    # -------------------------
    st.subheader("Raw Emotional Events")

    events = controller.emotional_memory.events
    if events:
        events_df = pd.DataFrame([
            {
                "Label": e.get("label"),
                "Intensity": round(e.get("intensity", 0.0), 3),
                "Timestamp": e.get("timestamp"),
            }
            for e in events
        ])
        st.table(events_df)
    else:
        st.write("No events yet.")

    # -------------------------
    # Test Run Log
    # -------------------------
    st.subheader("Test Run Log")

    log = st.session_state.get("test_log", [])
    if log:
        df = pd.DataFrame(log)
        st.table(df)
    else:
        st.write("No test runs yet.")

    # -------------------------
    # Mode Timeline
    # -------------------------
    st.subheader("Mode Timeline")

    mode_history = st.session_state.get("mode_history", [])
    if mode_history:
        df = pd.DataFrame(mode_history)
        df["Index"] = range(1, len(df) + 1)

        st.write("Mode History Table")
        st.table(df)

        chart_df = df[["Index", "Mode"]].copy()
        mode_map = {m: i for i, m in enumerate(chart_df["Mode"].unique())}
        chart_df["ModeValue"] = chart_df["Mode"].map(mode_map)

        st.write("Mode Timeline Chart")
        st.line_chart(chart_df.set_index("Index")["ModeValue"])

        st.write("Mode Legend:")
        st.json(mode_map)
    else:
        st.write("No mode history yet.")

    # -------------------------
    # Jury Diagnostics
    # -------------------------
    st.subheader("Jury Diagnostics")

    final = getattr(controller, "last_final_proposal", None)
    if not final:
        st.info("No Jury decision available yet.")
        return

    meta = final.get("metadata", {})
    all_scores = meta.get("jury_all_scores", {})