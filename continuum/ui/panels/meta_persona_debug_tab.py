# continuum/ui/panels/meta_persona_debug_tab.py

import streamlit as st

from continuum.debug.meta_persona_panel import MetaPersonaDebugPanel
from continuum.meta.aria_emotional_blending import compute_aria_style
from continuum.persona.voiceprint_loader import voiceprint_loader
from continuum.validators.voiceprint_validator import validate_output

from continuum.ui.panels.components.rewrite_diff_viewer import render_rewrite_diff_viewer
from continuum.ui.panels.components.emotional_trend_charts import render_emotional_trend_charts
from continuum.ui.panels.components.voiceprint_heatmap import render_voiceprint_heatmap
from continuum.ui.panels.components.actor_fusion_trace import render_actor_fusion_trace
from continuum.ui.panels.components.memory_timeline import render_memory_timeline


def render_meta_persona_debug_tab(controller):
    st.title("Meta‑Persona Debug (EI‑2.0)")

    emotional_state = getattr(controller, "last_emotional_state", None)
    emotional_memory = getattr(controller, "last_emotional_memory", None)
    meta = getattr(controller, "meta_persona", None)
    context = getattr(controller, "context", None)

    if emotional_state is None or emotional_memory is None:
        st.info("No emotional state available yet. Send a message to begin.")
        return

    if meta is None:
        st.error("Meta‑Persona engine not available.")
        return

    # Core debug panel (textual)
    dominant = meta._compute_dominant_emotion(emotional_state)
    memory_mods = emotional_memory.get_modifiers() if hasattr(emotional_memory, "get_modifiers") else {}
    style = compute_aria_style(emotional_state)

    if memory_mods:
        style["warmth"] += memory_mods.get("warmth_boost", 0)
        style["clarity"] += memory_mods.get("clarity_boost", 0)
        style["softness"] += memory_mods.get("grounding_boost", 0)
        style["brevity"] += memory_mods.get("pacing_slowdown", 0)

    report = None
    if context and context.debug_flags.get("validate_voiceprint"):
        report = validate_output(
            "debug-sample",
            emotional_state.as_dict(),
            voiceprint_loader.voiceprint,
        )

    panel = MetaPersonaDebugPanel()
    debug_text = panel.render(
        emotional_state,
        emotional_memory,
        style,
        memory_mods,
        dominant,
        voiceprint_loader,
        report,
    )

    st.subheader("Core Meta‑Persona Debug Panel")
    st.text(debug_text)

    st.markdown("---")

    # Structured sub‑sections
    render_rewrite_diff_viewer(controller)
    render_emotional_trend_charts(controller, emotional_state, emotional_memory)
    render_voiceprint_heatmap(controller, emotional_state, style)
    render_actor_fusion_trace(controller)
    render_memory_timeline(controller, emotional_memory)