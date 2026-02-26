"""
SQLAlchemy-based memory backend for persistent storage.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import select, delete, and_, or_
from typing import List, Optional, Any
import asyncio
from datetime import datetime, timezone
import json
from ..memory import (
    MemoryInterface,
    UserProperty,
    ConversationSession,
    ConversationMessage,
)
from ..models.database import (
    UserPropertyModel,
    ConversationMessageModel,
    ConversationSessionModel,
    Base as DatabaseBase,
)


class SQLMemoryBackend(MemoryInterface):
    """SQLAlchemy-based memory storage for persistent data"""

    def __init__(self, database_url: str, echo: bool = False):
        self.database_url = database_url
        self.echo = echo
        self.engine = None
        self.SessionLocal = None
        self._initialized = False

    async def _initialize(self):
        """Initialize database connection and create tables"""
        if self._initialized:
            return

        # Create async engine
        self.engine = create_async_engine(
            self.database_url,
            echo=self.echo,
            future=True,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False, future=True
        )

        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(DatabaseBase.metadata.create_all)

        self._initialized = True

    async def _get_session(self):
        """Get database session"""
        if not self._initialized:
            await self._initialize()

        async with self.SessionLocal() as session:
            yield session

    def _convert_to_user_property(self, model: UserPropertyModel) -> UserProperty:
        """Convert SQLAlchemy model to UserProperty"""
        return UserProperty(
            user_id=model.user_id,
            key=model.key,
            value=model.value,
            type=model.type,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _convert_to_conversation_session(
        self, model: ConversationSessionModel
    ) -> ConversationSession:
        """Convert SQLAlchemy model to ConversationSession"""
        return ConversationSession(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            created_at=model.created_at,
            updated_at=model.updated_at,
            messages=[],  # Will be loaded separately
            context=model.context,
            status=model.status.value,
        )

    def _convert_to_conversation_message(
        self, model: ConversationMessageModel
    ) -> ConversationMessage:
        """Convert SQLAlchemy model to ConversationMessage"""
        return ConversationMessage(
            id=model.id,
            user_id=model.user_id,
            session_id=model.session_id,
            message=model.message,
            role=model.role,
            timestamp=model.timestamp,
            extra_metadata=model.extra_metadata,
        )

    async def get_user_property(self, user_id: str, key: str) -> Optional[UserProperty]:
        """Get user property"""
        async for session in self._get_session():
            stmt = select(UserPropertyModel).where(
                and_(UserPropertyModel.user_id == user_id, UserPropertyModel.key == key)
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return self._convert_to_user_property(model)
            return None

    async def set_user_property(self, property: UserProperty) -> None:
        """Set user property"""
        async for session in self._get_session():
            # Check if property exists
            existing = await self.get_user_property(property.user_id, property.key)

            if existing:
                # Update existing property
                stmt = select(UserPropertyModel).where(
                    and_(
                        UserPropertyModel.user_id == property.user_id,
                        UserPropertyModel.key == property.key,
                    )
                )
                result = await session.execute(stmt)
                model = result.scalar_one()

                model.value = property.value
                model.type = property.type
                model.updated_at = datetime.now(timezone.utc)
            else:
                # Create new property
                model = UserPropertyModel(
                    user_id=property.user_id,
                    key=property.key,
                    value=property.value,
                    type=property.type,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                session.add(model)

            await session.commit()

    async def get_user_properties(self, user_id: str) -> List[UserProperty]:
        """Get all user properties"""
        async for session in self._get_session():
            stmt = select(UserPropertyModel).where(UserPropertyModel.user_id == user_id)
            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._convert_to_user_property(model) for model in models]

    async def get_conversation_session(
        self, session_id: str
    ) -> Optional[ConversationSession]:
        """Get conversation session with messages"""
        async for session in self._get_session():
            # Get session model
            stmt = (
                select(ConversationSessionModel)
                .where(ConversationSessionModel.id == session_id)
                .options(selectinload(ConversationSessionModel.messages))
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if not model:
                return None

            # Convert to ConversationSession
            conversation_session = self._convert_to_conversation_session(model)

            # Add messages
            conversation_session.messages = [
                self._convert_to_conversation_message(msg_model)
                for msg_model in model.messages
            ]

            return conversation_session

    async def create_conversation_session(self, session: ConversationSession) -> str:
        """Create conversation session"""
        async for db_session in self._get_session():
            # Create session model
            model = ConversationSessionModel(
                id=session.id,
                user_id=session.user_id,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                context=session.context,
                status=session.status,
            )

            db_session.add(model)
            await db_session.commit()

            # Add messages
            for message in session.messages:
                msg_model = ConversationMessageModel(
                    id=message.id,
                    user_id=message.user_id,
                    session_id=message.session_id,
                    message=message.message,
                    role=message.role,
                    timestamp=message.timestamp,
                    extra_metadata=message.extra_metadata,
                )
                db_session.add(msg_model)

            await db_session.commit()

            return session.id

    async def update_conversation_session(self, session: ConversationSession) -> None:
        """Update conversation session"""
        async for db_session in self._get_session():
            # Get existing session
            stmt = select(ConversationSessionModel).where(
                ConversationSessionModel.id == session.id
            )
            result = await db_session.execute(stmt)
            model = result.scalar_one_or_none()

            if not model:
                raise ValueError(f"Session {session.id} not found")

            # Update session
            model.title = session.title
            model.context = session.context
            model.status = session.status
            model.updated_at = datetime.now(timezone.utc)

            # Update messages (clear and recreate)
            await db_session.execute(
                delete(ConversationMessageModel).where(
                    ConversationMessageModel.session_id == session.id
                )
            )

            for message in session.messages:
                msg_model = ConversationMessageModel(
                    id=message.id,
                    user_id=message.user_id,
                    session_id=message.session_id,
                    message=message.message,
                    role=message.role,
                    timestamp=message.timestamp,
                    extra_metadata=message.extra_metadata,
                )
                db_session.add(msg_model)

            await db_session.commit()

    async def get_user_sessions(self, user_id: str) -> List[ConversationSession]:
        """Get all conversation sessions for a user"""
        async for session in self._get_session():
            # Get sessions
            stmt = (
                select(ConversationSessionModel)
                .where(ConversationSessionModel.user_id == user_id)
                .options(selectinload(ConversationSessionModel.messages))
            )
            result = await session.execute(stmt)
            models = result.scalars().all()

            # Convert to ConversationSession
            sessions = []
            for model in models:
                conversation_session = self._convert_to_conversation_session(model)
                conversation_session.messages = [
                    self._convert_to_conversation_message(msg_model)
                    for msg_model in model.messages
                ]
                sessions.append(conversation_session)

            return sessions

    async def add_message_to_session(
        self, session_id: str, message: ConversationMessage
    ) -> None:
        """Add message to conversation session"""
        async for db_session in self._get_session():
            # Create message model
            msg_model = ConversationMessageModel(
                id=message.id,
                user_id=message.user_id,
                session_id=message.session_id,
                message=message.message,
                role=message.role,
                timestamp=message.timestamp,
                extra_metadata=message.extra_metadata,
            )

            db_session.add(msg_model)

            # Update session timestamp
            stmt = select(ConversationSessionModel).where(
                ConversationSessionModel.id == session_id
            )
            result = await db_session.execute(stmt)
            session_model = result.scalar_one_or_none()

            if session_model:
                session_model.updated_at = datetime.now(timezone.utc)

            await db_session.commit()
