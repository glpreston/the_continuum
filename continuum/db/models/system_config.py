# continuum/db/models/system_config.py

from sqlalchemy import (
    Column, Integer, String, TIMESTAMP
)
from datetime import datetime
from continuum.db.models.base import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), nullable=False, unique=True)
    config_value = Column(String(500), nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)