"""Relevance analysis model for chatbot query-response evaluation."""

from sqlalchemy import Column, String, Text, Float, DateTime, Integer, Index, JSON, ForeignKey
from sqlalchemy.sql import func

from shared.database import Base


class RelevanceAnalysis(Base):
    """Stores relevance scoring results for chatbot query-response pairs."""

    __tablename__ = "relevance_analyses"

    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    relevance_score = Column(Float, nullable=False, default=0.0, index=True)
    analysis_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_relevance_analyses_session_id", "session_id"),
        Index("idx_relevance_analyses_user_id", "user_id"),
        Index("idx_relevance_analyses_relevance_score", "relevance_score"),
        {"mysql_engine": "InnoDB"},
    )
