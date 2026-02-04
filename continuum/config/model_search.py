# continuum/config/model_search.py

import requests
from datetime import datetime
from sqlalchemy import text
from continuum.db.sqlalchemy_connection import get_db_session


def refresh_node(node_id, endpoint):
    """
    Syncs model metadata from a node's /api/tags endpoint into MySQL.
    Modernized version:
    - Updates global model metadata in `models`
    - Updates node/model mapping in `model_nodes`
    - Removes legacy writes to node_model_metadata
    """

    base = endpoint.rstrip("/")
    url = f"{base}/api/tags"

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    db = get_db_session()
    conn = db.connection()

    try:
        for model in data.get("models", []):
            name = model["name"]
            details = model.get("details", {})

            # Parse modified_at if present
            modified_at = None
            if "modified_at" in model:
                try:
                    modified_at = datetime.fromisoformat(
                        model["modified_at"].replace("Z", "+00:00")
                    )
                except:
                    modified_at = None

            # 1. Ensure model exists in global models table
            conn.execute(
                text("""
                    INSERT INTO models (name)
                    VALUES (:name)
                    ON DUPLICATE KEY UPDATE name = name;
                """),
                {"name": name}
            )

            # Retrieve model_id
            result = conn.execute(
                text("SELECT id FROM models WHERE name = :name"),
                {"name": name}
            )
            model_id = result.fetchone()[0]

            # 2. Update global model metadata
            conn.execute(
                text("""
                    UPDATE models
                    SET
                        size = :size,
                        digest = :digest,
                        format = :format,
                        family = :family,
                        parameter_size = :parameter_size,
                        quantization_level = :quantization_level,
                        parent_model = :parent_model,
                        modified_at = :modified_at
                    WHERE id = :model_id;
                """),
                {
                    "model_id": model_id,
                    "size": model.get("size"),
                    "digest": model.get("digest"),
                    "format": details.get("format"),
                    "family": details.get("family"),
                    "parameter_size": details.get("parameter_size"),
                    "quantization_level": details.get("quantization_level"),
                    "parent_model": details.get("parent_model"),
                    "modified_at": modified_at,
                }
            )

            # 3. Ensure model_nodes entry exists
            conn.execute(
                text("""
                    INSERT INTO model_nodes (node_id, model_id)
                    VALUES (:node_id, :model_id)
                    ON DUPLICATE KEY UPDATE node_id = node_id;
                """),
                {"node_id": node_id, "model_id": model_id}
            )

        db.commit()

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()