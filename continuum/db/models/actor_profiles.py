# continuum/db/models/actor_profiles.py

from sqlalchemy import (
    Column, Integer, String, TIMESTAMP
)
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime
from continuum.db.models.base import Base


class ActorProfile(Base):
    __tablename__ = "actor_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_name = Column(String(100), nullable=False, unique=True)
    capability = Column(String(100), nullable=False)     # creative, logical, etc.
    preferred_tags = Column(JSON)                        # ["creative", "long-context"]
    persona = Column(JSON)                               # persona card
    created_at = Column(TIMESTAMP, default=datetime.utcnow)