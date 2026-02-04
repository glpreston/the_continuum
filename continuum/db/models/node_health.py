# continuum/db/models/node_health.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
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
    node_id = Column(Integer, ForeignKey("nodes.id"), unique=True, nullable=False)

    # Matches: timestamp timestamp NULL DEFAULT CURRENT_TIMESTAMP
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Matches: latency_ms int DEFAULT NULL
    latency_ms = Column(Integer)

    # Matches: status varchar(50) DEFAULT NULL
    status = Column(String(50))

    # Matches: health_score double DEFAULT '1'
    health_score = Column(Float, default=1.0)

    # Matches: failure_count int DEFAULT '0'
    failure_count = Column(Integer, default=0)

    # Matches: success_count int DEFAULT '0'
    success_count = Column(Integer, default=0)

    # Matches: failure_streak int DEFAULT '0'
    failure_streak = Column(Integer, default=0)

    # Matches: success_streak int DEFAULT '0'
    success_streak = Column(Integer, default=0)

    # Matches: quarantined int DEFAULT '0'
    quarantined = Column(Integer, default=0)

    # Matches: last_error text
    last_error = Column(Text)

    # Matches: last_heartbeat_at timestamp NULL DEFAULT CURRENT_TIMESTAMP
    last_heartbeat_at = Column(DateTime, default=datetime.utcnow)

    # Matches: updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to Node model
    node = relationship("Node", back_populates="health_records")