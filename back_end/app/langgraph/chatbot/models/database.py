"""
SQLAlchemy models for PA System database.
Handles user properties, conversation history, and session management.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    JSON,
    ForeignKey,
    Enum,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from datetime import datetime
import uuid
import enum

Base = declarative_base()


class PropertyType(enum.Enum):
    PREFERENCE = "preference"
    SETTING = "setting"
    CONTEXT = "context"
    PROFILE = "profile"


class SessionStatus(enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    CLOSED = "closed"


class UserPropertyModel(Base):
    """User property and preference data"""

    __tablename__ = "user_properties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(JSON, nullable=False)
    type = Column(Enum(PropertyType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Composite index for user_id and key
    __table_args__ = {"extend_existing": True}

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "key": self.key,
            "value": self.value,
            "type": self.type.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ConversationMessageModel(Base):
    """Conversation messages"""

    __tablename__ = "conversation_messages"

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(
        String(255), ForeignKey("conversation_sessions.id"), nullable=False, index=True
    )
    message = Column(Text, nullable=False)
    role = Column(String(50), nullable=False)  # 'user', 'assistant'
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    extra_metadata = Column(JSON, nullable=True)

    # Relationship with session
    session = relationship("ConversationSessionModel", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "message": self.message,
            "role": self.role,
            "timestamp": self.timestamp.isoformat(),
            "extra_metadata": self.extra_metadata or {},
        }


class ConversationSessionModel(Base):
    """Conversation sessions"""

    __tablename__ = "conversation_sessions"

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    context = Column(JSON, nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False)

    # Relationship with messages
    messages = relationship(
        "ConversationMessageModel",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "context": self.context or {},
            "status": self.status.value,
            "message_count": len(self.messages) if hasattr(self, "messages") else 0,
        }


class UserSessionSummary(Base):
    """User session summary for quick access"""

    __tablename__ = "user_session_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    last_message = Column(Text, nullable=True)
    last_message_time = Column(DateTime, nullable=True)
    total_messages = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "last_message": self.last_message,
            "last_message_time": self.last_message_time.isoformat()
            if self.last_message_time
            else None,
            "total_messages": self.total_messages,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
