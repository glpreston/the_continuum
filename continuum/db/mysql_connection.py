
# continuum/db/mysql_connection.py
import mysql.connector
from mysql.connector import pooling
import json


class MySQLConfigDB:
    """
    Connection layer for Aira's configuration database.
    Uses a connection pool for efficiency and thread safety.
    """

    def __init__(self,
                 host: str,
                 port: int,
                 user: str,
                 password: str,
                 database: str,
                 pool_name: str = "aira_pool",
                 pool_size: int = 5):

        self.pool = pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            pool_reset_session=True,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

    def get_conn(self):
        """Get a pooled connection."""
        return self.pool.get_connection()

    # -----------------------------
    # Generic helpers
    # -----------------------------

    def fetch_all(self, query, params=None):
        conn = self.get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def fetch_one(self, query, params=None):
        conn = self.get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row

    def execute(self, query, params=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        cursor.close()
        conn.close()

    def get_nodes(self):
        """
        Returns all nodes from the nodes table.
        Expected schema:
            id
            hostname
            endpoint
            models_json
            status
            last_heartbeat
        """
        query = """
            SELECT id, hostname, endpoint, models_json, status, last_heartbeat
            FROM nodes
        """

        conn = self.get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Normalize into Python dicts
        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "name": row["hostname"],
                "base_url": row["endpoint"],
                "models": row["models_json"],   # JSON array already parsed by MySQL driver
                "status": row["status"],
                "last_heartbeat": row["last_heartbeat"],
            })

        return result


    # -----------------------------
    # Domain-specific loaders
    # -----------------------------

    def load_nodes(self):
        return self.fetch_all("SELECT * FROM nodes")

    def load_actors(self):
        rows = self.fetch_all("SELECT * FROM actors")
        for r in rows:
            r["personality_json"] = json.loads(r["personality_json"])
        return rows

    def load_models(self):
        return self.fetch_all("SELECT * FROM models")

    def load_system_settings(self):
        rows = self.fetch_all("SELECT * FROM system_settings")
        settings = {}
        for r in rows:
            settings[r["setting_key"]] = json.loads(r["setting_value"])
        return settings

    def load_persona_presets(self):
        rows = self.fetch_all("SELECT * FROM persona_presets")
        for r in rows:
            r["config_json"] = json.loads(r["config_json"])
        return rows

    # -----------------------------
    # Node registry helpers
    # -----------------------------

    def update_node_heartbeat(self, node_id):
        self.execute(
            "UPDATE nodes SET last_heartbeat = NOW(), status = 'online' WHERE id = %s",
            (node_id,)
        )

    def register_node(self, hostname, endpoint, models_json):
        self.execute(
            """
            INSERT INTO nodes (hostname, endpoint, models_json, status, last_heartbeat)
            VALUES (%s, %s, %s, 'online', NOW())
            """,
            (hostname, endpoint, json.dumps(models_json))
        )