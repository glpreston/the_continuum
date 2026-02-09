#continuum/orchestrator/router/tests/conftest.py

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


# =========================================================
#  SQLite Test Database Fixture
# =========================================================
@pytest.fixture(scope="function")
def sqlite_db():
    """
    Creates a real in-memory SQLite database with the full schema.
    Returns a SQLAlchemy sessionmaker for use in tests.
    """

    engine = create_engine(
        DB_URL,
        pool_pre_ping=True,   # ping before use, auto-reconnect if dead
        pool_recycle=1800,    # recycle connections every 30 minutes
    )

    SessionLocal = sessionmaker(bind=engine)

    # -----------------------------------------------------
    # Create schema
    # -----------------------------------------------------
    schema_sql = """
    -- -------------------------
    -- nodes
    -- -------------------------
    CREATE TABLE nodes (
        id INTEGER PRIMARY KEY,
        name TEXT,
        type TEXT,
        host TEXT,
        provider TEXT,
        api_key_env TEXT,
        enabled INTEGER DEFAULT 1,
        status TEXT,
        last_seen TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- -------------------------
    -- node_health
    -- -------------------------
    CREATE TABLE node_health (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id INTEGER NOT NULL,
        latency_ms REAL,
        health_score REAL DEFAULT 1.0,
        failure_count INTEGER DEFAULT 0,
        success_count INTEGER DEFAULT 0,
        failure_streak INTEGER DEFAULT 0,
        success_streak INTEGER DEFAULT 0,
        quarantined INTEGER DEFAULT 0,
        last_error TEXT,
        last_heartbeat_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT,
        FOREIGN KEY (node_id) REFERENCES nodes(id)
    );

    CREATE UNIQUE INDEX idx_node_health_unique_node ON node_health(node_id);
    CREATE INDEX idx_node_health_quarantined ON node_health(quarantined);
    CREATE INDEX idx_node_health_health_score ON node_health(health_score);

    -- -------------------------
    -- model_nodes
    -- -------------------------
    CREATE TABLE model_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        node_id INTEGER NOT NULL,
        FOREIGN KEY (node_id) REFERENCES nodes(id)
    );

    CREATE INDEX idx_model_nodes_model ON model_nodes(model_name);
    CREATE INDEX idx_model_nodes_node ON model_nodes(node_id);

    -- -------------------------
    -- telemetry_config
    -- -------------------------
    CREATE TABLE telemetry_config (
        id INTEGER PRIMARY KEY,
        heartbeat_interval_seconds INTEGER,
        startup_warmup_minutes INTEGER,
        idle_timeout_minutes INTEGER,

        quarantine_threshold REAL,
        recovery_threshold REAL,

        staleness_penalty_seconds INTEGER,
        max_latency_ms_for_full_score INTEGER,
        max_latency_penalty REAL,

        failure_streak_penalty_per_failure REAL,
        max_failure_penalty REAL,

        success_streak_bonus_per_success REAL,
        max_success_bonus REAL
    );

    INSERT INTO telemetry_config (
        id,
        heartbeat_interval_seconds,
        startup_warmup_minutes,
        idle_timeout_minutes,
        quarantine_threshold,
        recovery_threshold,
        staleness_penalty_seconds,
        max_latency_ms_for_full_score,
        max_latency_penalty,
        failure_streak_penalty_per_failure,
        max_failure_penalty,
        success_streak_bonus_per_success,
        max_success_bonus
    ) VALUES (
        1,
        10,
        1,
        5,
        0.3,
        0.7,
        30,
        200,
        0.5,
        0.1,
        0.5,
        0.05,
        0.3
    );
    """

    with engine.begin() as conn:
        for statement in schema_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))        

    yield Session


# =========================================================
#  Factory Helpers
# =========================================================

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


def create_model_node(session, model_name, node_id):
    session.execute(
        text("""
            INSERT INTO model_nodes (model_name, node_id)
            VALUES (:model_name, :node_id)
        """),
        {"model_name": model_name, "node_id": node_id},
    )


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