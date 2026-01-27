# continuum/db/models/model_nodes.py

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Enum as SAEnum
from continuum.db.models.base import Base
from enum import Enum


class ModelAvailability(str, Enum):
    available = "available"
    unavailable = "unavailable"


class ModelNode(Base):
    __tablename__ = "model_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # MUST MATCH models.name EXACTLY
    model_name = Column(String(255), ForeignKey("models.name"), nullable=False)

    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)

    availability = Column(
        SAEnum(ModelAvailability),
        default=ModelAvailability.available,
        nullable=False,
    )

    last_updated = Column(TIMESTAMP, default=datetime.utcnow)

    notes = Column(String(5000))

    model = relationship("Model", back_populates="model_links")
    node = relationship("Node", back_populates="model_links")