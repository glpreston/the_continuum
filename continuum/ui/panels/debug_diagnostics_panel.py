# continuum/ui/panels/debug_diagnostics_panel.py
# for version EI-2.0

import streamlit as st
import pandas as pd

from continuum.meta.aria_emotional_blending import compute_aria_style
from continuum.debug.meta_persona_panel import MetaPersonaDebugPanel
from continuum.persona.voiceprint_loader import voiceprint_loader

def render_meta_persona_debug_tab(controller):
    ...

def render_debug_diagnostics(controller):
    st.title("Continuum Diagnostics")

    # ----------------------------------------------------------------------
    # Emotional Diagnostics (EI‑2.0)
    # ----------------------------------------------------------------------
    with st.expander("Emotional Diagnostics", expanded=True):
        memory = getattr(controller, "emotional_memory", None)

        if memory is None or not memory.events:
            st.info("No emotional events recorded yet.")
        else:
            payload = memory.get_debug_payload()

            # Summary metrics
            st.subheader("Summary")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Short‑Term Emotion", payload["short_term_emotion"])
            col2.metric("Long‑Term Emotion", payload["long_term_emotion"])
            col3.metric("Volatility", f"{payload['volatility']:.4f}")
            col4.metric("Confidence", f"{payload['confidence']:.4f}")

            st.markdown("---")

            # Smoothed EI‑2.0 state
            st.subheader("Smoothed Emotional State (EI‑2.0 Dimensions)")
            smoothed_df = pd.DataFrame(
                payload["smoothed_state"].items(),
                columns=["Dimension", "Intensity"],
            )
            st.dataframe(smoothed_df, use_container_width=True)

            # Trend
            st.subheader("Trend (Direction of Change)")
            trend_df = pd.DataFrame(
                payload["trend"].items(),
                columns=["Dimension", "Trend"],
            )
            st.dataframe(trend_df, use_container_width=True)

            st.markdown("---")

            # Recent events
            st.subheader("Recent Emotional Events")
            events_df = pd.DataFrame(payload["last_events"])
            st.dataframe(events_df, use_container_width=True)

    # ----------------------------------------------------------------------
    # Senate Diagnostics
    # ----------------------------------------------------------------------
    with st.expander("Senate Diagnostics", expanded=False):
        ranked = getattr(controller, "last_ranked_proposals", []) or []

        if not ranked:
            st.info("No Senate proposals available yet.")
        else:
            rows = []
            for idx, proposal in enumerate(ranked, start=1):
                rows.append(
                    {
                        "Rank": idx,
                        "Actor": proposal.get("actor", "unknown"),
                        "Score": proposal.get("score", None),
                        "Reason": proposal.get("reason", ""),
                        "Text": proposal.get("text", ""),
                    }
                )

            df = pd.DataFrame(rows)
            st.subheader("Ranked Proposals")
            st.dataframe(df, use_container_width=True)

    # ----------------------------------------------------------------------
    # Jury Diagnostics
    # ----------------------------------------------------------------------
    with st.expander("Jury Diagnostics", expanded=True):
        final = getattr(controller, "last_final_proposal", None)
        if not final:
            st.info("No Jury decision available yet.")
        else:
            meta = final.get("metadata", {}) or {}
            all_scores = meta.get("jury_all_scores", {}) or {}
            winner = final.get("actor", "unknown")

            st.subheader("Decision Summary")
            st.write(f"**Winner:** `{winner}`")

            if "jury_reasoning" in meta:
                with st.expander("Jury Explanation"):
                    st.write(meta["jury_reasoning"])

            if "jury_dissent" in meta:
                with st.expander("Jury Dissent"):
                    st.write(meta["jury_dissent"])

            if all_scores:
                df = pd.DataFrame(all_scores).T
                if "total" in df.columns:
                    df = df.sort_values("total", ascending=False)

                st.subheader("Per‑Actor Rubric Scores")
                st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)

                st.subheader("Winner Breakdown")
                st.json(all_scores.get(winner, {}))

    # ----------------------------------------------------------------------
    # Turn Timeline
    # ----------------------------------------------------------------------
    with st.expander("Turn Timeline", expanded=False):
        history = getattr(controller, "turn_history", []) or []

        if not history:
            st.info("No turns recorded yet.")
        else:
            rows = []
            for idx, turn in enumerate(history, start=1):
                emotion = turn.get("emotion", {}) or {}
                final_proposal = turn.get("final_proposal", {}) or {}

                rows.append(
                    {
                        "Turn": idx,
                        "User": turn.get("user", ""),
                        "Emotion Label": emotion.get("label", ""),
                        "Emotion Intensity": emotion.get("intensity", 0.0),
                        "Winning Actor": final_proposal.get("actor", "unknown"),
                        "Assistant (Meta‑Persona)": turn.get("assistant", ""),
                    }
                )

            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)

    # ----------------------------------------------------------------------
    # Controller Flow / Tool Logs
    # ----------------------------------------------------------------------
    with st.expander("Controller Flow & Tool Logs", expanded=False):
        tool_logs = getattr(controller, "tool_logs", []) or []

        if not tool_logs:
            st.info("No tool logs recorded yet.")
        else:
            normalized = [
                entry if isinstance(entry, dict) else {"entry": str(entry)}
                for entry in tool_logs
            ]

            df = pd.DataFrame(normalized)
            st.dataframe(df, use_container_width=True)


    # ----------------------------------------------------------------------
    # Meta‑Persona Debug Panel (EI‑2.0 Internal State)
    # ----------------------------------------------------------------------
    with st.expander("Meta‑Persona Debug Panel", expanded=False):
        context = getattr(controller, "context", None)
        meta = getattr(controller, "meta_persona", None)

        if context is None or meta is None:
            st.info("Meta‑Persona context not available.")
        else:
            # We need the emotional state + memory from the controller
            emotional_state = getattr(controller, "last_emotional_state", None)
            emotional_memory = getattr(controller, "emotional_memory", None)

            if emotional_state is None or emotional_memory is None:
                st.info("No emotional state available for Meta‑Persona.")
            else:
                # Compute the same values MetaPersona.render() uses
                dominant = meta._compute_dominant_emotion(emotional_state)
                memory_mods = emotional_memory.get_modifiers() if hasattr(emotional_memory, "get_modifiers") else {}
                style = compute_aria_style(emotional_state)

                # Apply memory modifiers to style (same as render())
                if memory_mods:
                    style["warmth"] += memory_mods.get("warmth_boost", 0)
                    style["clarity"] += memory_mods.get("clarity_boost", 0)
                    style["softness"] += memory_mods.get("grounding_boost", 0)
                    style["brevity"] += memory_mods.get("pacing_slowdown", 0)

                # Optional validator report
                report = None
                if context.debug_flags.get("validate_voiceprint"):
                    report = validate_output(
                        "debug-sample",
                        emotional_state.as_dict(),
                        voiceprint_loader.voiceprint,
                    )

                # Render the panel
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

                st.text(debug_text)
                
    # ----------------------------------------------------------------------
    # Meta‑Persona Output Trace
    # ----------------------------------------------------------------------
    with st.expander("Meta‑Persona Output Trace", expanded=False):
        context = getattr(controller, "context", None)

        if context is None:
            st.info("No context available.")
        else:
            messages = getattr(context, "messages", [])
            last_raw = getattr(controller, "last_raw_actor_output", None)

            if last_raw:
                st.subheader("Last Raw Actor Output")
                st.write(last_raw)

            if messages:
                st.subheader("Recent Conversation Messages")
                rows = [
                    {"Role": msg.role, "Content": msg.content}
                    for msg in messages[-10:]
                ]
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No messages recorded in context yet.")