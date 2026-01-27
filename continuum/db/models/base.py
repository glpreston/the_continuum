# continuum/db/models/base.py

from sqlalchemy.orm import declarative_base

# Shared SQLAlchemy declarative base for all ORM models
Base = declarative_base()