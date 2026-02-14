"""Confidence score model for chatbot response quality tracking."""

from sqlalchemy import Column, String, Float, DateTime, Integer, Index, JSON, ForeignKey
from sqlalchemy.sql import func

from shared.database import Base


class ConfidenceScore(Base):
    """Stores confidence scoring results for chatbot responses."""

    __tablename__ = "confidence_scores"

    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    confidence_value = Column(Float, nullable=False, default=0.0, index=True)
    confidence_level = Column(String(20), nullable=False)
    source_factors = Column(JSON, nullable=True)
    calculated_at = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_confidence_scores_session_id", "session_id"),
        Index("idx_confidence_scores_user_id", "user_id"),
        Index("idx_confidence_scores_confidence_value", "confidence_value"),
        {"mysql_engine": "InnoDB"},
    )
