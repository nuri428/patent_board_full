"""
Patent Analysis Model

Stores patent analysis results with multi-source patent support.
Supports analysis from KIPRIS, USPTO, EPO, KIPO, WIPO, JPO, CNIPA, and other sources.
"""

from sqlalchemy import Column, String, Float, Integer, Text, DateTime, Index, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from shared.database import Base
import enum


class PatentSource(str, enum.Enum):
    """Patent source enumerations"""
    KIPRIS = "kipris"
    USPTO = "uspto"
    EPO = "epo"
    KIPO = "kipo"
    WIPO = "wipo"
    JPO = "jpo"
    CNIPA = "cnipa"
    OTHER = "other"


class PatentSourceType(str, enum.Enum):
    """Patent source type enumerations"""
    PATENT = "patent"
    DOCUMENT = "document"
    OTHER = "other"


class PatentAnalysis(Base):
    """Patent analysis results stored in MariaDB"""

    __tablename__ = "patent_analyses"

    # Primary key
    id = Column(String(36), primary_key=True)  # UUID

    # Reference to session
    session_id = Column(String(36), nullable=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    # Multi-source patent support
    analyzed_patents = Column(JSON, nullable=True)  # Array of patent objects from all sources
    patent_source = Column(String(20), nullable=True)  # PatentSource enum value

    # Analysis results
    confidence_score = Column(Float, default=0.5, index=True)  # 0.0 to 1.0
    relevant_sections = Column(JSON, nullable=True)  # List of relevant sections

    # Metadata
    analysis_metadata = Column(JSON, nullable=True)  # Additional analysis metadata
    source_type = Column(String(20), nullable=True, default=PatentSourceType.PATENT.value)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)

    # Relationships
    # Note: No direct relationship to ArchivedSession to avoid circular dependencies
    # Session reference is via session_id string

    # Indexes
    __table_args__ = (
        Index("idx_patent_analyses_user_id", "user_id"),
        Index("idx_patent_analyses_session_id", "session_id"),
        Index("idx_patent_analyses_patent_source", "patent_source"),
        Index("idx_patent_analyses_source_type", "source_type"),
        Index("idx_patent_analyses_confidence", "confidence_score"),
        {"mysql_engine": "InnoDB"},
    )
