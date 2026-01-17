# continuum/db/models/models.py

from sqlalchemy import (
    Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.dialects.mysql import JSON
from continuum.db.models.base import Base


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    name = Column(String(200), nullable=False)
    size_gb = Column(DECIMAL(10, 2))
    tags = Column(JSON)                      # ["creative", "coder", "vision"]
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)

    node = relationship("Node", back_populates="models")