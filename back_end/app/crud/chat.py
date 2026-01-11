from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from app.models import ChatSession, ChatMessage
from app.schemas import ChatSessionCreate, ChatMessageCreate
import json
import uuid


class ChatCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_session(self, session_id: int) -> Optional[ChatSession]:
        """Get chat session by ID with messages"""
        result = await self.db.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_session_by_uuid(self, session_uuid: str) -> Optional[ChatSession]:
        """Get chat session by UUID with messages"""
        result = await self.db.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.session_id == session_uuid)
        )
        return result.scalar_one_or_none()

    async def get_user_sessions(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[ChatSession]:
        """Get user's chat sessions"""
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(desc(ChatSession.updated_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_session(
        self, user_id: int, session_create: ChatSessionCreate
    ) -> ChatSession:
        """Create new chat session"""
        # Generate unique session ID
        session_uuid = str(uuid.uuid4())

        db_session = ChatSession(
            session_id=session_uuid,
            user_id=user_id,
            title=session_create.title or "New Chat",
            is_active=session_create.is_active,
        )

        self.db.add(db_session)
        await self.db.commit()
        await self.db.refresh(db_session)
        return db_session

    async def update_session(
        self,
        session_id: int,
        title: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[ChatSession]:
        """Update chat session"""
        db_session = await self.get_session(session_id)
        if not db_session:
            return None

        if title is not None:
            db_session.title = title
        if is_active is not None:
            db_session.is_active = is_active

        await self.db.commit()
        await self.db.refresh(db_session)
        return db_session

    async def delete_session(self, session_id: int, user_id: int) -> bool:
        """Delete chat session (verify ownership)"""
        db_session = await self.db.execute(
            select(ChatSession).where(
                and_(ChatSession.id == session_id, ChatSession.user_id == user_id)
            )
        )
        session = db_session.scalar_one_or_none()

        if not session:
            return False

        await self.db.delete(session)
        await self.db.commit()
        return True

    async def add_message(self, message_create: ChatMessageCreate) -> ChatMessage:
        """Add message to chat session"""
        # Update session's updated_at timestamp
        await self.db.execute(
            select(ChatSession).where(ChatSession.id == message_create.session_id)
        )

        db_message = ChatMessage(
            session_id=message_create.session_id,
            message_type=message_create.message_type,
            content=message_create.content,
            patent_references=json.dumps(message_create.patent_references)
            if message_create.patent_references
            else None,
            sources=json.dumps(message_create.sources)
            if message_create.sources
            else None,
        )

        self.db.add(db_message)

        # Update session timestamp
        session = await self.get_session(message_create.session_id)
        if session:
            # This will be handled by database triggers or manually
            pass

        await self.db.commit()
        await self.db.refresh(db_message)
        return db_message

    async def get_session_messages(
        self, session_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChatMessage]:
        """Get messages in a session"""
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_last_message(
        self, session_id: int, message_type: Optional[str] = None
    ) -> Optional[ChatMessage]:
        """Get last message in session"""
        query = select(ChatMessage).where(ChatMessage.session_id == session_id)
        if message_type:
            query = query.where(ChatMessage.message_type == message_type)

        query = query.order_by(desc(ChatMessage.timestamp)).limit(1)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def count_session_messages(
        self, session_id: int, message_type: Optional[str] = None
    ) -> int:
        """Count messages in session"""
        query = select(func.count(ChatMessage.id)).where(
            ChatMessage.session_id == session_id
        )
        if message_type:
            query = query.where(ChatMessage.message_type == message_type)

        result = await self.db.execute(query)
        return result.scalar()

    async def search_sessions(
        self, user_id: int, query: str, limit: int = 10
    ) -> List[ChatSession]:
        """Search user's sessions by title or content"""
        result = await self.db.execute(
            select(ChatSession)
            .where(
                and_(
                    ChatSession.user_id == user_id,
                    ChatSession.title.ilike(f"%{query}%"),
                )
            )
            .order_by(desc(ChatSession.updated_at))
            .limit(limit)
        )
        return result.scalars().all()


# Helper function to get chat CRUD instance
def get_chat_crud(db: AsyncSession) -> ChatCRUD:
    return ChatCRUD(db)
