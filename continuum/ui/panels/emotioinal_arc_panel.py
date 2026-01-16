# debug/emotional_arc_panel.py

import streamlit as st
import pandas as pd
from typing import Any, Dict, List


def classify_emotional_arc(history: List[Dict[str, Any]]) -> str:
    """
    Very simple emotional arc classifier based on start/end values.
    This can be upgraded later once the emotional arc engine is richer.
    """
    if len(history) < 3:
        return "Insufficient data for arc classification"

    def slope(key: str) -> float:
        start = history[0]["state"].get(key, 0.0)
        end = history[-1]["state"].get(key, 0.0)
        return end - start

    curiosity_slope = slope("curiosity")
    tension_slope = slope("tension")
    calm_slope = slope("calm")

    if curiosity_slope > 0.15:
        return "Rising Curiosity Arc"
    if tension_slope > 0.15:
        return "Rising Tension Arc"
    if calm_slope > 0.15:
        return "Settling Calm Arc"
    if tension_slope < -0.15:
        return "Tension-Recovery Arc"

    return "Stable Emotional Arc"


def render_emotional_arc_panel(controller: Any) -> None:
    """
    Render the Emotional Arc Debug Panel.

    Expects (eventually):
      - controller.emotional_arc_history: List[{
            "turn": int,
            "state": {emotion_name: float, ...},
            "dominant": str,
            "volatility": float,
            "confidence": float,
            "fusion_weights": Optional[Dict[str, float]],
        }]
    """
    st.markdown("## 🌈 Emotional Arc Timeline")

    #history: List[Dict[str, Any]] = getattr(controller, "emotional_arc_history", [])
    history = controller.emotional_arc_engine.get_history()
    if not history:
        st.info("No emotional arc data available yet. "
                "Once emotional_arc_history is wired, this panel will come alive.")
        return

    # ---------------------------------------------------------
    # Emotional Timeline (per emotion)
    # ---------------------------------------------------------
    st.markdown("### Emotional Intensity Over Turns")

    emotion_rows = []
    for h in history:
        row = {"turn": h.get("turn", 0)}
        state = h.get("state", {})
        for k, v in state.items():
            row[k] = v
        emotion_rows.append(row)

    if emotion_rows:
        df_emotions = pd.DataFrame(emotion_rows).set_index("turn")
        st.line_chart(df_emotions, height=250)
    else:
        st.warning("Emotional state data is missing from history entries.")

    # ---------------------------------------------------------
    # Dominant Emotion Timeline
    # ---------------------------------------------------------
    st.markdown("### Dominant Emotion Per Turn")

    dominants = [h.get("dominant", "unknown") for h in history]
    st.write(" → ".join(dominants))

    # ---------------------------------------------------------
    # Volatility Curve
    # ---------------------------------------------------------
    st.markdown("### Volatility Over Time")

    vol_rows = [
        {"turn": h.get("turn", 0), "volatility": h.get("volatility", 0.0)}
        for h in history
    ]
    df_vol = pd.DataFrame(vol_rows).set_index("turn")
    st.line_chart(df_vol, height=150)

    # ---------------------------------------------------------
    # Emotional Arc Classification
    # ---------------------------------------------------------
    st.markdown("### Current Emotional Arc")

    arc_label = classify_emotional_arc(history)
    st.success(f"**{arc_label}**")

    # ---------------------------------------------------------
    # Fusion Influence Trace
    # ---------------------------------------------------------
    st.markdown("### Fusion Influence Over Time")

    fusion_rows = []
    for h in history:
        base = {"turn": h.get("turn", 0)}
        fw = h.get("fusion_weights") or {}
        for actor_name, weight in fw.items():
            base[actor_name] = weight
        fusion_rows.append(base)

    if any(len(r) > 1 for r in fusion_rows):  # more than just "turn"
        df_fusion = pd.DataFrame(fusion_rows).set_index("turn")
        st.area_chart(df_fusion, height=200)
    else:
        st.info("Fusion weights not yet recorded in emotional_arc_history. "
                "Once wired, this section will show actor blending over time.")