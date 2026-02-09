import streamlit as st
import pandas as pd
from .state import EmotionalState
from .timeline import EmotionalArcTimeline
from .memory import EmotionalMemoryEngine

class EmotionalDebugPanel:

    def __init__(self, state: EmotionalState, timeline: EmotionalArcTimeline, memory: EmotionalMemoryEngine):
        self.state = state
        self.timeline = timeline
        self.memory = memory

    def render(self):
        st.subheader("🧠 Emotional Engine Diagnostics")

        # ---------------------------------------------------------
        # 1. Current Emotional State
        # ---------------------------------------------------------
        st.markdown("### Current Emotional State")
        st.json({
            "emotion": self.state.current_emotion,
            "intensity": round(self.state.intensity, 3),
            "baseline": self.state.baseline,
            "volatility": self.state.volatility,
            "decay_rate": self.state.decay_rate,
            "last_user_emotion": self.state.last_user_emotion,
        })

        # ---------------------------------------------------------
        # 2. Emotional Sparkline
        # ---------------------------------------------------------
        st.markdown("### Emotional Intensity Sparkline")

        if self.timeline.points:
            df = pd.DataFrame({
                "timestamp": [p.timestamp for p in self.timeline.points],
                "intensity": [p.intensity for p in self.timeline.points]
            })
            df = df.set_index("timestamp")
            st.line_chart(df)
        else:
            st.info("No emotional data recorded yet.")

        # ---------------------------------------------------------
        # 3. Momentum
        # ---------------------------------------------------------
        st.markdown("### Emotional Momentum")
        momentum = self.timeline.get_momentum()
        st.write(momentum if momentum is not None else "No momentum yet")

        # ---------------------------------------------------------
        # 4. Short-Term Emotional Memory
        # ---------------------------------------------------------
        st.markdown("### Short-Term Emotional Memory")
        st.json({
            "lingering_mood": self.memory.get_lingering_mood(),
            "recent_states": [
                {"emotion": p.emotion, "intensity": p.intensity}
                for p in self.memory.short_term
            ]
        })

        # ---------------------------------------------------------
        # 5. Long-Term Emotional Bias
        # ---------------------------------------------------------
        st.markdown("### Long-Term Emotional Bias")
        st.json(self.memory.long_term)

        # ---------------------------------------------------------
        # 6. Drift Detection
        # ---------------------------------------------------------
        st.markdown("### Drift Detection")

        bias = self.memory.get_long_term_bias()
        if bias and bias != self.state.baseline:
            st.warning(f"Emotional drift detected: trending toward **{bias}**")
        else:
            st.success("No emotional drift detected.")