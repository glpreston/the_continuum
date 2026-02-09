# continuum/db/models/user_preferences.py

from sqlalchemy import (
    Column, Integer, String, TIMESTAMP, ForeignKey
)
from datetime import datetime
from continuum.db.models.base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(String(500), nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)