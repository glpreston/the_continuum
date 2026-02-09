# continuum/ui/pages/3_Telemetry.py

import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text

from continuum.orchestrator.continuum_controller import ContinuumController
from continuum.orchestrator.router.node_discovery import discover_live_models


#@st.cache_resource
#def get_controller():
    #return ContinuumController()

if "controller" not in st.session_state:
    st.session_state.controller = ContinuumController()

controller = st.session_state.controller

def _safe_round(value, digits=3):
    if value is None:
        return None
    try:
        return round(float(value), digits)
    except Exception:
        return None


def _compute_cluster_health(node_health_rows):
    if not node_health_rows:
        return 0.0, "NO DATA"

    scores = [nh.health_score for nh in node_health_rows if nh.health_score is not None]
    if not scores:
        return 0.0, "NO DATA"

    avg_score = sum(scores) / len(scores)
    quarantined = sum(1 for nh in node_health_rows if nh.quarantined)

    penalty = min(0.3, quarantined * 0.05)
    cluster_score = max(0.0, avg_score - penalty)

    if cluster_score >= 0.8:
        status = "HEALTHY"
    elif cluster_score >= 0.5:
        status = "DEGRADED"
    else:
        status = "CRITICAL"

    return cluster_score, status


#def main():
    #st.set_page_config(page_title="Telemetry", layout="wide")
    #controller = get_controller()

def main():
    st.set_page_config(page_title="Cognitive Trace", layout="wide")

    # Use the shared controller from session_state
    #if "controller" not in st.session_state:
    #    st.session_state.controller = ContinuumController()

    #controller = st.session_state.controller

    st.title("📡 Telemetry — Cluster, Nodes, Models, Routing")

    # -------------------------------------------------------------------------
    # Guard: telemetry available?
    # -------------------------------------------------------------------------
    if not hasattr(controller, "node_health_store") or controller.node_health_store is None:
        st.warning("Telemetry is not initialized or HeartbeatManager failed to start.")
        return

    node_health_rows = controller.node_health_store.get_all()

    if not node_health_rows:
        st.info("No telemetry data yet. Heartbeat warmup may still be running.")
        return

    # -------------------------------------------------------------------------
    # 1. Cluster Health Summary
    # -------------------------------------------------------------------------
    st.subheader("🟢 Cluster Health Summary")

    cluster_score, cluster_status = _compute_cluster_health(node_health_rows)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cluster Health Score", _safe_round(cluster_score, 3))
    with col2:
        st.metric("Status", cluster_status)
    with col3:
        st.metric("Nodes Monitored", len(node_health_rows))

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 2. Node Health Overview (table)
    # -------------------------------------------------------------------------
    st.subheader("🟠 Node Health Overview")

    node_table = []
    for nh in node_health_rows:
        node_table.append({
            "Node ID": nh.node_id,
            "Health Score": _safe_round(nh.health_score),
            "Status": nh.status,
            "Latency (ms)": _safe_round(nh.latency_ms),
            "Failure Streak": nh.failure_streak,
            "Success Streak": nh.success_streak,
            "Quarantined": bool(nh.quarantined),
            "Last Heartbeat": nh.last_heartbeat_at,
            "Last Error": nh.last_error,
        })

    st.dataframe(pd.DataFrame(node_table), width='stretch')

    # -------------------------------------------------------------------------
    # 3. Node-by-Node Detail View
    # -------------------------------------------------------------------------
    st.subheader("🟣 Node Detail View")

    for nh in node_health_rows:
        title = f"Node {nh.node_id} — {nh.status} (Q={bool(nh.quarantined)})"
        with st.expander(title):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Health Score", _safe_round(nh.health_score))
                st.metric("Latency (ms)", _safe_round(nh.latency_ms))
            with col2:
                st.metric("Failure Streak", nh.failure_streak)
                st.metric("Success Streak", nh.success_streak)
            with col3:
                st.metric("Quarantined", "Yes" if nh.quarantined else "No")
                if isinstance(nh.last_heartbeat_at, datetime):
                    ts = nh.last_heartbeat_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    ts = str(nh.last_heartbeat_at)
                st.metric("Last Heartbeat", ts)

            if nh.last_error:
                st.write("Last Error:")
                st.code(nh.last_error)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 4. Model Health Overview (Live Discovery + Telemetry)
    # -------------------------------------------------------------------------
    st.subheader("🔵 Model Health Overview")

    try:
        live_models = discover_live_models()
    except Exception as e:
        st.error(f"Failed to discover live models: {e}")
        live_models = []

    if not live_models:
        st.info("No live models discovered.")
    else:
        # Build lookup: node_name -> node_id
        node_name_to_id = {
            n.name: n.id
            for n in controller.registry.get_all_nodes()
        }

        # Group models by name
        models_by_name = {}
        for lm in live_models:
            models_by_name.setdefault(lm.name, []).append(lm)

        model_table = []
        for model_name, instances in models_by_name.items():
            node_count = len(instances)

            health_scores = []
            quarantined_nodes = 0

            for inst in instances:
                node_id = node_name_to_id.get(inst.node)
                if node_id is None:
                    continue

                nh = next((h for h in node_health_rows if h.node_id == node_id), None)
                if nh:
                    if nh.health_score is not None:
                        health_scores.append(nh.health_score)
                    if nh.quarantined:
                        quarantined_nodes += 1

            avg_health = sum(health_scores) / len(health_scores) if health_scores else 1.0

            model_table.append({
                "Model": model_name,
                "Nodes": node_count,
                "Avg Health": _safe_round(avg_health),
                "Quarantined Nodes": quarantined_nodes,
            })

        st.dataframe(pd.DataFrame(model_table), width='stretch')
        
    st.markdown("---")

    # -------------------------------------------------------------------------
    # 5. Health Score Timeline
    # -------------------------------------------------------------------------
    st.subheader("📈 Health Score Timeline (Last Snapshot)")

    timeline_df = pd.DataFrame([
        {"Node ID": nh.node_id, "Health Score": nh.health_score or 0.0}
        for nh in node_health_rows
    ]).set_index("Node ID")

    st.bar_chart(timeline_df, width='stretch')

    # -------------------------------------------------------------------------
    # 6. Quarantine Snapshot
    # -------------------------------------------------------------------------
    st.subheader("🚨 Quarantine Snapshot")

    quarantine_df = pd.DataFrame([
        {"Node ID": nh.node_id, "Quarantined": 1 if nh.quarantined else 0}
        for nh in node_health_rows
    ]).set_index("Node ID")

    st.bar_chart(quarantine_df, width='stretch')

    st.markdown("---")

    # -------------------------------------------------------------------------
    # 7. Model-level Routing Simulator
    # -------------------------------------------------------------------------
    st.subheader("🧪 Model-level Routing Simulator")

    intent = st.text_input("Intent (for classifier)", value="conversation")
    actor = st.text_input("Actor (optional)", value="Architect")

    if st.button("Simulate Routing"):
        try:
            routing_decision = controller.router.route(
                user_text=f"[SIMULATION] intent={intent}",
                actor_name=actor or None,
                extra_context={"simulation": True},
            )
            st.write("Routing Decision:")
            st.json(routing_decision)
        except Exception as e:
            st.error(f"Routing simulation failed: {e}")

    # -------------------------------------------------------------------------
    # 8. Recent Routing Decision Inspector
    # -------------------------------------------------------------------------
    st.subheader("🟠 Recent Routing Decision")

    if getattr(controller, "last_routing_decision", None):
        st.json(controller.last_routing_decision)
    else:
        st.write("No routing decisions recorded yet.")


if __name__ == "__main__":
    main()