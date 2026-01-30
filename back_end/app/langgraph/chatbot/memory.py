"""
Memory management system for the chatbot.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import pickle
import uuid
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod


@dataclass
class UserProperty:
    """User preference and property data"""

    user_id: str
    key: str
    value: Any
    type: str  # 'preference', 'setting', 'context', 'profile'
    created_at: datetime
    updated_at: datetime


@dataclass
class ConversationMessage:
    """Single conversation message"""

    id: str
    user_id: str
    session_id: str
    message: str
    role: str  # 'user', 'assistant'
    timestamp: datetime
    extra_metadata: Union[Dict[str, Any], None] = None


@dataclass
class ConversationSession:
    """User conversation session"""

    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ConversationMessage]
    context: Union[Dict[str, Any], None] = None
    status: str = "active"  # 'active', 'archived'


class MemoryInterface(ABC):
    """Abstract interface for memory storage"""

    @abstractmethod
    async def get_user_property(self, user_id: str, key: str) -> Optional[UserProperty]:
        pass

    @abstractmethod
    async def set_user_property(self, property: UserProperty) -> None:
        pass

    @abstractmethod
    async def get_user_properties(self, user_id: str) -> List[UserProperty]:
        pass

    @abstractmethod
    async def get_conversation_session(
        self, session_id: str
    ) -> Optional[ConversationSession]:
        pass

    @abstractmethod
    async def create_conversation_session(self, session: ConversationSession) -> str:
        pass

    @abstractmethod
    async def update_conversation_session(self, session: ConversationSession) -> None:
        pass

    @abstractmethod
    async def get_user_sessions(self, user_id: str) -> List[ConversationSession]:
        pass

    @abstractmethod
    async def add_message_to_session(
        self, session_id: str, message: ConversationMessage
    ) -> None:
        pass


class MemoryManager:
    """Main memory manager combining multiple storage backends"""

    def __init__(
        self,
        primary_backend: MemoryInterface,
        cache_backend: Optional[MemoryInterface] = None,
    ):
        self.primary = primary_backend
        self.cache = cache_backend
        self._cache_ttl = timedelta(hours=1)

    async def get_user_property(self, user_id: str, key: str) -> Optional[UserProperty]:
        """Get user property with cache fallback"""
        if self.cache:
            cached = await self.cache.get_user_property(user_id, key)
            if cached:
                return cached

        property_data = await self.primary.get_user_property(user_id, key)

        if self.cache and property_data:
            await self.cache.set_user_property(property_data)

        return property_data

    async def set_user_property(self, property: UserProperty) -> None:
        """Set user property"""
        await self.primary.set_user_property(property)

        if self.cache:
            await self.cache.set_user_property(property)

    async def get_user_properties(self, user_id: str) -> List[UserProperty]:
        """Get all user properties"""
        return await self.primary.get_user_properties(user_id)

    async def get_conversation_session(
        self, session_id: str
    ) -> Optional[ConversationSession]:
        """Get conversation session"""
        if self.cache:
            cached = await self.cache.get_conversation_session(session_id)
            if cached:
                return cached

        session = await self.primary.get_conversation_session(session_id)

        if self.cache and session:
            await self.primary.update_conversation_session(session)

        return session

    async def create_conversation_session(self, session: ConversationSession) -> str:
        """Create new conversation session"""
        session_id = await self.primary.create_conversation_session(session)

        if self.cache:
            session.id = session_id
            await self.cache.create_conversation_session(session)

        return session_id

    async def update_conversation_session(self, session: ConversationSession) -> None:
        """Update conversation session"""
        await self.primary.update_conversation_session(session)

        if self.cache:
            await self.cache.update_conversation_session(session)

    async def get_user_sessions(self, user_id: str) -> List[ConversationSession]:
        """Get all user sessions"""
        return await self.primary.get_user_sessions(user_id)

    async def add_message_to_session(
        self, session_id: str, message: ConversationMessage
    ) -> None:
        """Add message to conversation session"""
        await self.primary.add_message_to_session(session_id, message)

        # Update cache if available
        if self.cache:
            session = await self.cache.get_conversation_session(session_id)
            if session:
                session.messages.append(message)
                session.updated_at = datetime.utcnow()
                await self.cache.update_conversation_session(session)
