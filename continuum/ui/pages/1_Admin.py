# continuum/ui/pages/1_Admin.py
import streamlit as st
import pandas as pd
from sqlalchemy import text

from continuum.orchestrator.continuum_controller import ContinuumController
from continuum.orchestrator.router.node_discovery import discover_live_models
# ---------------------------------------------------------
# Shared Controller (persistent across all pages)
# ---------------------------------------------------------
if "controller" not in st.session_state:
    st.session_state.controller = ContinuumController()

controller = st.session_state.controller

if st.button("Reload Controller"):
    # Reset the controller explicitly
    st.session_state.controller = ContinuumController()
    st.experimental_rerun()


# ---------------------------------------------------------
# Main Page
# ---------------------------------------------------------
def main():
    st.set_page_config(page_title="Admin", layout="wide")

    # controller is already available globally
    # no need to reinitialize it here
    controller = st.session_state.controller

    # Always refresh registry on page load
    controller.registry.refresh()

    st.title("⚙️ Admin — Nodes, Models, Persona, System Settings")
    
    # =========================================================
    # 1. NODE REGISTRY
    # =========================================================
    st.subheader("🖥️ Node Registry")

    try:
        node_rows = controller.registry.get_all_nodes()
    except Exception:
        node_rows = []

    if not node_rows:
        st.info("No nodes registered.")
    else:
        node_table = []
        for n in node_rows:
            node_table.append({
                "Node Name": n.name,
                "Host": n.host,
                "Type": getattr(n.type, "value", n.type),
                "Enabled": n.enabled,
                "Status": getattr(n.status, "value", n.status),
                "Last Seen": n.last_seen,
            })

        st.dataframe(pd.DataFrame(node_table), width='stretch')

    st.markdown("---")

    # =========================================================
    # 2. NODE HEALTH QUICK VIEW
    # =========================================================
    st.subheader("🩺 Node Health Quick View")

    try:
        health_rows = controller.node_health_store.get_all()
    except Exception:
        health_rows = []

    if health_rows:
        health_table = []
        for nh in health_rows:
            health_table.append({
                "Node ID": nh.node_id,
                "Health Score": nh.health_score,
                "Status": nh.status,
                "Latency (ms)": nh.latency_ms,
                "Quarantined": bool(nh.quarantined),
                "Last Heartbeat": nh.last_heartbeat_at,
            })

        st.dataframe(pd.DataFrame(health_table), width='stretch')
    else:
        st.info("No health data yet.")

    st.markdown("---")

    # =========================================================
    # 3. LIVE MODEL INVENTORY (replaces DB-backed Model Registry)
    # =========================================================
    st.subheader("📦 Live Model Inventory (from Nodes)")

    try:
        live_models = discover_live_models()
    except Exception as e:
        st.error(f"Failed to discover live models: {e}")
        live_models = []

    if not live_models:
        st.info("No live models discovered from any node.")
    else:
        model_table = []
        for lm in live_models:
            model_table.append({
                "Model Name": lm.name,
                "Node": lm.node,
                "Avg Health": lm.avg_health,
                "Quarantined": lm.quarantined,
                "Required Memory (GB)": lm.required_memory_gb,
                "Node Max Memory (GB)": lm.max_node_memory_gb,
                "Vision Model": lm.is_vision,
            })

        st.dataframe(pd.DataFrame(model_table), width='stretch')

    st.markdown("---")

    # =========================================================
    # 4. MODEL → NODE ASSIGNMENT
    # =========================================================
    st.subheader("🔗 Model → Node Assignment")

    with st.expander("Edit Model Assignments"):
        # Model names come from live discovery
        model_names = sorted({lm.name for lm in live_models})

        node_objects = controller.registry.get_all_nodes()
        node_labels = [
            f"{n.name} ({n.host}) — ID {n.id}"
            for n in node_objects
        ]

        selected_model = st.selectbox("Select Model", model_names)
        selected_node_label = st.selectbox("Assign to Node", node_labels)

        selected_node_id = int(selected_node_label.split("ID ")[1])

        if st.button("Assign Model to Node"):
            try:
                controller.registry.assign_model_to_node(selected_model, selected_node_id)
                st.success(f"Assigned {selected_model} to node {selected_node_id}")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed: {e}")

    st.markdown("---")

    # =========================================================
    # 5. REWRITE MODEL CONFIG
    # =========================================================
    st.subheader("🌀 Rewrite Model Configuration")

    current_rewrite = controller.rewrite_model
    st.write(f"**Current Rewrite Model:** `{current_rewrite}`")

    new_model = st.text_input("Set New Rewrite Model", value=current_rewrite)

    if st.button("Update Rewrite Model"):
        try:
            controller.rewrite_model = new_model
            controller.db.execute(
                text("UPDATE rewrite_config SET pinned_model = :m"),
                {"m": new_model},
            )
            controller.db.commit()
            st.success(f"Rewrite model updated to {new_model}")
        except Exception as e:
            st.error(f"Failed: {e}")

    st.markdown("---")

    # =========================================================
    # 6. PERSONA SETTINGS
    # =========================================================
    st.subheader("🎨 Aira Persona Settings")

    col1, col2 = st.columns(2)

    with col1:
        temperature = st.slider("Temperature", 0.0, 2.0, controller.temperature, 0.05)
        max_tokens = st.number_input("Max Tokens", 64, 4096, controller.max_tokens)

    with col2:
        style = st.selectbox("Voice Style", ["neutral", "warm", "formal", "playful"])
        rewrite_depth = st.slider("Max Rewrite Depth", 1, 10, controller.max_rewrite_depth)

    if st.button("Save Persona Settings"):
        controller.temperature = temperature
        controller.max_tokens = max_tokens
        controller.voiceprint["style"] = style
        controller.max_rewrite_depth = rewrite_depth
        st.success("Persona settings updated.")

    st.markdown("---")

    # =========================================================
    # 7. SYSTEM ACTIONS
    # =========================================================
    st.subheader("🛠️ System Actions")

    colA, colB, colC = st.columns(3)

    with colA:
        if st.button("Trigger Heartbeat Warmup"):
            if controller.heartbeat:
                controller.heartbeat.on_system_start()
                st.success("Heartbeat warmup triggered.")
            else:
                st.error("HeartbeatManager not available.")

    with colB:
        if st.button("Probe All Nodes Now"):
            if controller.heartbeat:
                controller.heartbeat._probe_all_nodes()
                st.success("Probe triggered.")
            else:
                st.error("HeartbeatManager not available.")

    with colC:
        if st.button("Shutdown Heartbeat"):
            if controller.heartbeat:
                controller.heartbeat.stop()
                st.success("Heartbeat stopped.")
            else:
                st.error("HeartbeatManager not available.")


if __name__ == "__main__":
    main()