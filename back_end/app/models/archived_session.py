from sqlalchemy import Column, String, Text, DateTime, Integer, Index
from sqlalchemy.sql import func
from shared.database import Base


class ArchivedSession(Base):
    """Archived chat sessions stored in MariaDB"""

    __tablename__ = "archived_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), unique=True, nullable=False, index=True)  # UUID
    user_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    messages = Column(Text, nullable=True)  # JSON array of messages
    context = Column(Text, nullable=True)  # JSON object of context
    created_at = Column(DateTime, default=func.now(), nullable=False)
    archived_at = Column(DateTime, default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_archived_sessions_user_id", "user_id"),
        Index("idx_archived_sessions_session_id", "session_id"),
        {"mysql_engine": "InnoDB"},
    )
