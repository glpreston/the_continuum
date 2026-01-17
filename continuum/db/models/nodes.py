# continuum/db/models/nodes.py

from sqlalchemy import (
    Column, Integer, String, Boolean, Enum, TIMESTAMP
)
from sqlalchemy.orm import relationship
from datetime import datetime
from continuum.db.models.base import Base
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
    host = Column(String(255))               # Ollama or custom endpoint
    provider = Column(String(100))           # Cloud provider name
    api_key_env = Column(String(100))        # Env var storing API key
    enabled = Column(Boolean, default=True)
    status = Column(Enum(NodeStatus), default=NodeStatus.unknown)
    last_seen = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    models = relationship("Model", back_populates="node", cascade="all, delete")
    health_records = relationship("NodeHealth", back_populates="node", cascade="all, delete")