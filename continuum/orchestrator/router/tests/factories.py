# content of continuum/orchestrator/router/tests/factories.py
from sqlalchemy import text


# ---------------------------------------------------------
# Insert a node into the nodes table
# ---------------------------------------------------------
def create_node(
    session,
    node_id,
    name=None,
    enabled=True,
    status="healthy",
    host="localhost",
    provider="local",
    api_key_env=None,
):
    session.execute(
        text("""
            INSERT INTO nodes (
                id, name, type, host, provider, api_key_env, enabled, status
            ) VALUES (
                :id, :name, 'local', :host, :provider, :api_key_env, :enabled, :status
            )
        """),
        {
            "id": node_id,
            "name": name or f"node-{node_id}",
            "host": host,
            "provider": provider,
            "api_key_env": api_key_env,
            "enabled": 1 if enabled else 0,
            "status": status,
        },
    )


# ---------------------------------------------------------
# Insert a node_health row
# ---------------------------------------------------------
def create_node_health(
    session,
    node_id,
    latency_ms=100,
    health_score=1.0,
    failure_count=0,
    success_count=0,
    failure_streak=0,
    success_streak=0,
    quarantined=0,
    last_error=None,
    status="ok",
):
    session.execute(
        text("""
            INSERT INTO node_health (
                node_id,
                latency_ms,
                health_score,
                failure_count,
                success_count,
                failure_streak,
                success_streak,
                quarantined,
                last_error,
                status
            ) VALUES (
                :node_id,
                :latency_ms,
                :health_score,
                :failure_count,
                :success_count,
                :failure_streak,
                :success_streak,
                :quarantined,
                :last_error,
                :status
            )
        """),
        {
            "node_id": node_id,
            "latency_ms": latency_ms,
            "health_score": health_score,
            "failure_count": failure_count,
            "success_count": success_count,
            "failure_streak": failure_streak,
            "success_streak": success_streak,
            "quarantined": quarantined,
            "last_error": last_error,
            "status": status,
        },
    )


# ---------------------------------------------------------
# Insert a model → node mapping
# ---------------------------------------------------------
def create_model_node(session, model_name, node_id):
    session.execute(
        text("""
            INSERT INTO model_nodes (model_name, node_id)
            VALUES (:model_name, :node_id)
        """),
        {"model_name": model_name, "node_id": node_id},
    )


# ---------------------------------------------------------
# High-level convenience: create a fully wired node
# ---------------------------------------------------------
def create_full_node(
    session,
    node_id,
    model_name,
    *,
    enabled=True,
    status="healthy",
    latency_ms=100,
    health_score=1.0,
    quarantined=0,
    health_status="ok",
):
    """
    Creates:
    - nodes row
    - node_health row
    - model_nodes row

    Perfect for integration tests.
    """

    create_node(
        session,
        node_id=node_id,
        enabled=enabled,
        status=status,
    )

    create_node_health(
        session,
        node_id=node_id,
        latency_ms=latency_ms,
        health_score=health_score,
        quarantined=quarantined,
        status=health_status,
    )

    create_model_node(session, model_name, node_id)