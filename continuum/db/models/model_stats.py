# continuum/db/models/model_stats.py

from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from datetime import datetime
from continuum.db.models.base import Base

class ModelStats(Base):
    __tablename__ = "model_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(255), nullable=False)
    actor_role = Column(String(255), nullable=True)

    success_rate = Column(Float, default=0.0)
    avg_latency_ms = Column(Integer, default=0)
    avg_cost_per_call = Column(Float, default=0.0)

    total_calls = Column(Integer, default=0)
    total_failures = Column(Integer, default=0)

    last_updated = Column(
        TIMESTAMP,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )