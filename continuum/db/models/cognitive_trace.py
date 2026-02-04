# continuum/db/models/cognitive_trace.py

from sqlalchemy import Column, Integer, Float, String, Boolean, Text, JSON, TIMESTAMP, text
from continuum.db.models.base import Base


class CognitiveTrace(Base):
    __tablename__ = "cognitive_trace"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    actor_name = Column(String(100))
    model_name = Column(String(200))
    node_name = Column(String(200))

    routing_time = Column(Float)      # optional / currently unused
    actor_time = Column(Float)        # optional / currently unused
    senate_time = Column(Float)
    jury_time = Column(Float)
    fusion_time = Column(Float)
    rewrite_time = Column(Float)
    total_time = Column(Float)

    actor_confidence = Column(Float)
    actor_output_length = Column(Integer)

    jury_winner = Column(String(100))
    jury_scores = Column(JSON)        # can be NULL for now

    rewrite_delta = Column(Integer)

    error_flag = Column(Boolean, default=False)
    error_message = Column(Text)