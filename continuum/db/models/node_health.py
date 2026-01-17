# continuum/db/models/node_health.py

from sqlalchemy import (
    Column, Integer, TIMESTAMP, Enum, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from continuum.db.models.base import Base
import enum


class HealthStatus(enum.Enum):
    online = "online"
    offline = "offline"
    degraded = "degraded"


class NodeHealth(Base):
    __tablename__ = "node_health"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    latency_ms = Column(Integer)
    status = Column(Enum(HealthStatus), nullable=False)

    node = relationship("Node", back_populates="health_records")