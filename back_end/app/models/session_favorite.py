from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    Integer,
    Index,
    JSON,
    ForeignKey,
)
from sqlalchemy.sql import func

from shared.database import Base


class SessionFavorite(Base):
    __tablename__ = "session_favorites"

    id = Column(String(36), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(36), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)
    is_pinned = Column(Boolean, default=False, nullable=False, index=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)

    __table_args__ = (
        Index("idx_session_favorites_user_id", "user_id"),
        Index("idx_session_favorites_session_id", "session_id"),
        Index("idx_session_favorites_pinned", "is_pinned"),
        Index("idx_session_favorites_user_session", "user_id", "session_id", unique=True),
        {"mysql_engine": "InnoDB"},
    )
