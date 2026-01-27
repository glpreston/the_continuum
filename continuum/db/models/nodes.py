# continuum/db/models/nodes.py

from sqlalchemy import (
    Column, Integer, String, Boolean, Enum, TIMESTAMP
)
from sqlalchemy.orm import relationship
from datetime import datetime
from continuum.db.models.base import Base
from continuum.db.models.node_health import NodeHealth
import enum


class NodeType(enum.Enum):
    ollama = "ollama"
    cloud = "cloud"
    custom = "custom"


class NodeStatus(enum.Enum):
    online = "online"
    offline = "offline"
    unknown = "unknown"



class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(NodeType), nullable=False)
    host = Column(String(255))
    provider = Column(String(100))
    api_key_env = Column(String(100))
    enabled = Column(Boolean, default=True)
    status = Column(Enum(NodeStatus), default=NodeStatus.unknown)
    last_seen = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    model_links = relationship("ModelNode", back_populates="node", cascade="all, delete")
    health_records = relationship("NodeHealth", back_populates="node", cascade="all, delete")

    @property
    def base_url(self):
        """
        Compute a usable base URL for this node.
        Adjust this logic depending on your actual node types.
        """
        if not self.host:
            return None

        # If host already looks like a URL, return it directly
        if self.host.startswith("http://") or self.host.startswith("https://"):
            return self.host.rstrip("/")

        # Default: assume http
        return f"http://{self.host}".rstrip("/")

