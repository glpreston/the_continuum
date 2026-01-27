# continuum/db/models/models.py

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from continuum.db.models.base import Base


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    provider = Column(String(255), nullable=False)
    context_window = Column(Integer)
    temperature_default = Column(Float)

    # Correct many-to-many relationship
    model_links = relationship("ModelNode", back_populates="model", cascade="all, delete")