# continuum/db/models/user_voiceprints.py

from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, LargeBinary
)
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.dialects.mysql import JSON
from continuum.db.models.base import Base


class UserVoiceprint(Base):
    __tablename__ = "user_voiceprints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    embedding = Column(LargeBinary)          # voiceprint data
    metadata = Column(JSON)                  # pitch, timbre, etc.
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User")