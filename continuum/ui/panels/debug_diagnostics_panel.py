# continuum/ui/panels/debug_diagnostics_panel.py
# for version EI-2.0

import streamlit as st
import pandas as pd


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
            # Flatten proposals into a table
            rows = []
            for idx, proposal in enumerate(ranked, start=1):
                actor = proposal.get("actor", "unknown")
                score = proposal.get("score", None)
                reason = proposal.get("reason", "")
                text = proposal.get("text", "")

                rows.append(
                    {
                        "Rank": idx,
                        "Actor": actor,
                        "Score": score,
                        "Reason": reason,
                        "Text": text,
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
                user = turn.get("user", "")
                emotion = turn.get("emotion", {}) or {}
                label = emotion.get("label", "")
                intensity = emotion.get("intensity", 0.0)
                final_proposal = turn.get("final_proposal", {}) or {}
                actor = final_proposal.get("actor", "unknown")
                assistant = turn.get("assistant", "")

                rows.append(
                    {
                        "Turn": idx,
                        "User": user,
                        "Emotion Label": label,
                        "Emotion Intensity": intensity,
                        "Winning Actor": actor,
                        "Assistant (Meta‑Persona)": assistant,
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
            # Expect each log to be a dict; if not, wrap
            normalized = []
            for entry in tool_logs:
                if isinstance(entry, dict):
                    normalized.append(entry)
                else:
                    normalized.append({"entry": str(entry)})

            df = pd.DataFrame(normalized)
            st.dataframe(df, use_container_width=True)

    # ----------------------------------------------------------------------
    # Meta‑Persona Output Trace
    # ----------------------------------------------------------------------
    with st.expander("Meta‑Persona Output Trace", expanded=False):
        context = getattr(controller, "context", None)

        if context is None:
            st.info("No context available.")
        else:
            # Show last few assistant messages and raw actor output if present
            messages = context.messages if hasattr(context, "messages") else []
            last_raw = getattr(controller, "last_raw_actor_output", None)

            if last_raw:
                st.subheader("Last Raw Actor Output")
                st.write(last_raw)

            if messages:
                st.subheader("Recent Conversation Messages")
                rows = []
                for msg in messages[-10:]:
                    rows.append(
                        {
                            "Role": getattr(msg, "role", ""),
                            "Content": getattr(msg, "content", ""),
                        }
                    )
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No messages recorded in context yet.")