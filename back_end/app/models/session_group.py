"""
Session Group Model

Manages session groups for organizing and categorizing chat sessions.
Supports group membership, tags, and color coding for visual organization.
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    Integer,
    Index,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from shared.database import Base


class SessionGroup(Base):
    """Session groups for organizing chat sessions"""

    __tablename__ = "session_groups"

    # Primary key
    id = Column(String(36), primary_key=True)  # UUID

    # Group information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    color_code = Column(String(10), default="#57373", nullable=False)  # Hex color code
    is_default = Column(Boolean, default=False, nullable=False)

    # Creator
    creator_user_id = Column(Integer, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)

    # Relationships
    # Note: Many-to-many relationship with users is handled through group_members association table
    # Note: One-to-many relationship with sessions is handled through session_group_id foreign key

    # Indexes
    __table_args__ = (
        Index("idx_session_groups_name", "name"),
        Index("idx_session_groups_creator", "creator_user_id"),
        Index("idx_session_groups_is_default", "is_default"),
        {"mysql_engine": "InnoDB"},
    )


class GroupMember(Base):
    """Association table for many-to-many relationship between groups and users"""

    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String(36), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    role = Column(String(50), default="member", nullable=False)  # owner, admin, member
    joined_at = Column(DateTime, default=func.now(), nullable=False)

    # Unique constraint: a user can only be added to a group once
    __table_args__ = (
        Index("idx_group_members_group_id", "group_id"),
        Index("idx_group_members_user_id", "user_id"),
        Index("idx_group_members_unique", "group_id", "user_id", unique=True),
        {"mysql_engine": "InnoDB"},
    )


class SessionGroupTag(Base):
    """Tags for session groups to enable categorization and filtering"""

    __tablename__ = "session_group_tags"

    id = Column(String(36), primary_key=True)  # UUID
    group_id = Column(String(36), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    color_code = Column(String(10), nullable=True)  # Hex color code for tag display

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_session_group_tags_group_id", "group_id"),
        Index("idx_session_group_tags_name", "name"),
        {"mysql_engine": "InnoDB"},
    )
