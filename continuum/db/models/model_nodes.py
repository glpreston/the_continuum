# continuum/db/models/model_nodes.py

from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, ForeignKey
from sqlalchemy.orm import relationship
from continuum.db.models.base import Base


class ModelNode(Base):
    __tablename__ = "model_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # NEW schema fields
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)

    status = Column(String(50), default="available")
    last_checked = Column(TIMESTAMP, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    model = relationship("Model", back_populates="model_links")
    node = relationship("Node", back_populates="model_links")