# continuum/db/models/user_memory.py

from sqlalchemy import (
    Column, Integer, String, TIMESTAMP, ForeignKey, Text
)
from datetime import datetime
from continuum.db.models.base import Base


class UserMemory(Base):
    __tablename__ = "user_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    memory_type = Column(String(100), nullable=False)   # fact, preference, event, emotion
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_accessed = Column(TIMESTAMP, default=datetime.utcnow)