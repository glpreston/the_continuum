# continuum/db/models/actor_profiles.py

from sqlalchemy.dialects.mysql import JSON
from continuum.db.models.base import Base

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    JSON,
    TIMESTAMP,
)
from sqlalchemy.sql import func
from datetime import datetime



from continuum.db.models.base import Base


class ActorProfile(Base):
    __tablename__ = "actor_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)

    actor_name = Column(String(100), nullable=False, unique=True)

    # NEW fields for full actor definition
    model_name = Column(String(200), nullable=False)
    fallback_model = Column(String(200), nullable=False)
    personality = Column(String(200), nullable=False)
    system_prompt = Column(Text)
    temperature_default = Column(Float, nullable=False)
    context_window = Column(Integer, nullable=False)
    role = Column(String(100), nullable=False)

    # Legacy persona metadata (still useful)
    capability = Column(String(100), nullable=True)
    preferred_tags = Column(JSON)
    persona = Column(JSON)

    # Modern SQLAlchemy timestamp (no utcnow deprecation)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
