# continuum/ui/pages/6_Model_Discovery.py

import streamlit as st
import requests
import pandas as pd

from sqlalchemy import text
from continuum.db.sqlalchemy_connection import get_db_session

# Import the live discovery function
from continuum.orchestrator.router.node_discovery import discover_live_models

API_BASE = "http://localhost:8000"


def refresh_node_api(node_id: int):
    """Call the FastAPI endpoint to refresh a node."""
    url = f"{API_BASE}/nodes/{node_id}/refresh"
    resp = requests.post(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_all_nodes():
    """Load nodes from DB (hostnames, enabled flags, etc.)."""
    db = get_db_session()
    conn = db.connection()

    result = (
        conn.execute(
            text(
                """
                SELECT
                    id,
                    name,
                    host,
                    enabled,
                    last_seen
                FROM nodes
                WHERE enabled = 1
                ORDER BY name ASC
                """
            )
        )
        .mappings()
        .all()
    )

    db.close()
    return result


# ---------------------------------------------------------
# Streamlit Page
# ---------------------------------------------------------

st.set_page_config(page_title="Model Discovery", layout="wide")
st.title("🔍 Model Discovery & Node Sync Dashboard")

st.write(
    "This page shows **live model discovery** from each node's `/api/tags` endpoint. "
    "It no longer uses the database for model metadata."
)

nodes = get_all_nodes()

# Load live model inventory once per page load
live_models = discover_live_models()

# ---------------------------------------------------------
# Refresh All Nodes
# ---------------------------------------------------------

st.subheader("Cluster Actions")

if st.button("🔄 Refresh All Nodes"):
    with st.spinner("Refreshing all nodes..."):
        for node in nodes:
            try:
                refresh_node_api(node["id"])
            except Exception as e:
                st.error(f"Failed to refresh node {node['name']}: {e}")
        st.success("All nodes refreshed successfully")

st.divider()

# ---------------------------------------------------------
# Per-Node Panels
# ---------------------------------------------------------

st.subheader("Node Model Inventory")

for node in nodes:
    # Prefer name over ID in UI
    node_title = f"🖥️ {node['name']}  —  {node['host']}"
    with st.expander(node_title, expanded=False):

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            status_label = "enabled" if node.get("enabled", 1) else "disabled"
            st.write(f"**Status:** {status_label}")
            st.write(f"**Last seen:** {node.get('last_seen')}")

        with col2:
            if st.button(f"Refresh {node['name']}", key=f"refresh_{node['id']}"):
                try:
                    with st.spinner(f"Refreshing {node['name']}..."):
                        _ = refresh_node_api(node["id"])
                    st.success(f"{node['name']} refreshed successfully")
                except Exception as e:
                    st.error(f"Error refreshing node: {e}")

        with col3:
            st.write("")  # spacing

        # Filter live models for this node
        node_models = [
            m for m in live_models
            if m.node.lower() == node["name"].lower()
        ]

        if not node_models:
            st.warning("No live models discovered on this node.")
            continue

        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "Model": m.name,
                "Node": m.node,  # name, not ID
                "Health": m.avg_health,
                "Quarantined": m.quarantined,
                "Vision": m.is_vision,
            }
            for m in node_models
        ])

        st.dataframe(df, width=True)