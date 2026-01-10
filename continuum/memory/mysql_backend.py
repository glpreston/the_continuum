"""
MySQL-backed memory store for The Continuum.
This is a drop-in replacement for MemoryStore, providing
persistent episodic and semantic memory using MySQL.

This is a stub: the structure is complete, and the queries
are ready, but you can expand it with indexing, embeddings,
or retrieval logic later.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import mysql.connector
from mysql.connector import Error


@dataclass
class MySQLMemoryBackend:
    host: str
    port: int
    user: str
    password: str
    database: str

    conn: Optional[mysql.connector.connection.MySQLConnection] = None

    def connect(self) -> None:
        """Establish a MySQL connection if not already connected."""
        if self.conn and self.conn.is_connected():
            return

        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True,
            )
        except Error as e:
            print(f"[MySQLMemoryBackend] Connection error: {e}")
            self.conn = None

    def ensure_schema(self) -> None:
        """Create tables if they do not exist."""
        self.connect()
        if not self.conn:
            return

        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodic_memory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                content TEXT NOT NULL,
                metadata JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS semantic_memory (
                mem_key VARCHAR(255) PRIMARY KEY,
                mem_value JSON NOT NULL,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        cursor.close()

    # -----------------------------
    # Episodic Memory
    # -----------------------------

    def add_episode(self, data: Dict[str, Any]) -> None:
        self.connect()
        if not self.conn:
            return

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO episodic_memory (content, metadata) VALUES (%s, %s)",
            (data.get("content", ""), str(data.get("metadata", {}))),
        )
        cursor.close()

    def recent_episodes(self, limit: int = 5) -> List[Dict[str, Any]]:
        self.connect()
        if not self.conn:
            return []

        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT content, metadata, timestamp FROM episodic_memory "
            "ORDER BY timestamp DESC LIMIT %s",
            (limit,),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows

    # -----------------------------
    # Semantic Memory
    # -----------------------------

    def add_semantic(self, key: str, value: Any) -> None:
        self.connect()
        if not self.conn:
            return

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO semantic_memory (mem_key, mem_value)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE mem_value = VALUES(mem_value)
            """,
            (key, str(value)),
        )
        cursor.close()

    def get_semantic(self, key: str) -> Any:
        self.connect()
        if not self.conn:
            return None

        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT mem_value FROM semantic_memory WHERE mem_key = %s",
            (key,),
        )
        row = cursor.fetchone()
        cursor.close()
        return row["mem_value"] if row else None