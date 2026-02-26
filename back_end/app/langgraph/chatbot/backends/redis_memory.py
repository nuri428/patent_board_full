"""
Redis-based memory backend for fast caching and session management.
"""

import json
import pickle
import redis.asyncio as redis
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
import asyncio
from ..memory import (
    MemoryInterface,
    UserProperty,
    ConversationSession,
    ConversationMessage,
)


class RedisMemoryBackend(MemoryInterface):
    """Redis-based memory storage with TTL support"""

    def __init__(self, redis_url: str = "redis://localhost:6379", ttl_hours: int = 24):
        self.redis_url = redis_url
        self.ttl = ttl_hours * 3600  # Convert to seconds
        self.redis_client = None
        self._lock = asyncio.Lock()

    async def _connect(self):
        """Connect to Redis"""
        if not self.redis_client:
            self.redis_client = redis.from_url(self.redis_url)

    async def _disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    def _serialize_user_property(self, prop: UserProperty) -> str:
        """Serialize user property to JSON"""
        data = {
            "key": prop.key,
            "value": prop.value,
            "type": prop.type,
            "created_at": prop.created_at.isoformat(),
            "updated_at": prop.updated_at.isoformat(),
        }
        return json.dumps(data)

    def _deserialize_user_property(self, data: str) -> UserProperty:
        """Deserialize user property from JSON"""
        json_data = json.loads(data)
        return UserProperty(
            key=json_data["key"],
            value=json_data["value"],
            type=json_data["type"],
            created_at=datetime.fromisoformat(json_data["created_at"]),
            updated_at=datetime.fromisoformat(json_data["updated_at"]),
        )

    def _serialize_conversation_session(self, session: ConversationSession) -> str:
        """Serialize conversation session to JSON"""
        data = {
            "id": session.id,
            "user_id": session.user_id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "context": session.context,
            "status": session.status,
        }

        # Convert messages to dict format
        messages_data = []
        for msg in session.messages:
            messages_data.append(
                {
                    "id": msg.id,
                    "user_id": msg.user_id,
                    "session_id": msg.session_id,
                    "message": msg.message,
                    "role": msg.role,
                    "timestamp": msg.timestamp.isoformat(),
                    "extra_metadata": msg.extra_metadata,
                }
            )
        data["messages"] = messages_data

        return json.dumps(data)

    def _deserialize_conversation_session(self, data: str) -> ConversationSession:
        """Deserialize conversation session from JSON"""
        json_data = json.loads(data)

        # Create messages
        messages = []
        for msg_data in json_data.get("messages", []):
            message = ConversationMessage(
                id=msg_data["id"],
                user_id=msg_data["user_id"],
                session_id=msg_data["session_id"],
                message=msg_data["message"],
                role=msg_data["role"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                metadata=msg_data.get("metadata", {}),
            )
            messages.append(message)

        return ConversationSession(
            id=json_data["id"],
            user_id=json_data["user_id"],
            title=json_data["title"],
            created_at=datetime.fromisoformat(json_data["created_at"]),
            updated_at=datetime.fromisoformat(json_data["updated_at"]),
            messages=messages,
            context=json_data.get("context", {}),
            status=json_data.get("status", "active"),
        )

    async def get_user_property(self, user_id: str, key: str) -> Optional[UserProperty]:
        """Get user property from Redis"""
        await self._connect()

        cache_key = f"user:{user_id}:properties:{key}"
        data = await self.redis_client.get(cache_key)

        if data:
            return self._deserialize_user_property(data)
        return None

    async def set_user_property(self, property: UserProperty) -> None:
        """Set user property in Redis"""
        await self._connect()

        cache_key = f"user:{property.user_id}:properties:{property.key}"
        data = self._serialize_user_property(property)
        await self.redis_client.setex(cache_key, self.ttl, data)

    async def get_user_properties(self, user_id: str) -> List[UserProperty]:
        """Get all user properties from Redis"""
        await self._connect()

        # Get all property keys for the user
        pattern = f"user:{user_id}:properties:*"
        keys = await self.redis_client.keys(pattern)

        if not keys:
            return []

        # Get all properties
        pipe = self.redis_client.pipeline()
        for key in keys:
            pipe.get(key)
        results = await pipe.execute()

        # Deserialize results
        properties = []
        for data in results:
            if data:
                properties.append(self._deserialize_user_property(data))

        return properties

    async def get_conversation_session(
        self, session_id: str
    ) -> Optional[ConversationSession]:
        """Get conversation session from Redis"""
        await self._connect()

        cache_key = f"session:{session_id}"
        data = await self.redis_client.get(cache_key)

        if data:
            return self._deserialize_conversation_session(data)
        return None

    async def create_conversation_session(self, session: ConversationSession) -> str:
        """Create conversation session in Redis"""
        await self._connect()

        cache_key = f"session:{session.id}"
        data = self._serialize_conversation_session(session)
        await self.redis_client.setex(cache_key, self.ttl, data)

        # Add to user's session list
        user_sessions_key = f"user:{session.user_id}:sessions"
        await self.redis_client.lpush(user_sessions_key, session.id)
        await self.redis_client.expire(user_sessions_key, self.ttl)

        return session.id

    async def update_conversation_session(self, session: ConversationSession) -> None:
        """Update conversation session in Redis"""
        await self._connect()

        cache_key = f"session:{session.id}"
        data = self._serialize_conversation_session(session)
        await self.redis_client.setex(cache_key, self.ttl, data)

    async def get_user_sessions(self, user_id: str) -> List[ConversationSession]:
        """Get all conversation sessions for a user from Redis"""
        await self._connect()

        # Get session IDs
        user_sessions_key = f"user:{user_id}:sessions"
        session_ids = await self.redis_client.lrange(user_sessions_key, 0, -1)

        if not session_ids:
            return []

        # Get sessions
        pipe = self.redis_client.pipeline()
        for session_id in session_ids:
            pipe.get(f"session:{session_id.decode()}")
        results = await pipe.execute()

        # Deserialize results
        sessions = []
        for data in results:
            if data:
                sessions.append(self._deserialize_conversation_session(data))

        return sessions

    async def add_message_to_session(
        self, session_id: str, message: ConversationMessage
    ) -> None:
        """Add message to conversation session in Redis"""
        await self._connect()

        # Get session
        session = await self.get_conversation_session(session_id)
        if session:
            session.messages.append(message)
            session.updated_at = datetime.now(timezone.utc)

            # Update session in Redis
            await self.update_conversation_session(session)

        # Update session summary
        summary_key = f"session:{session_id}:summary"
        await self.redis_client.hset(
            summary_key,
            mapping={
                "last_message": message.message[:500],  # Limit message length
                "last_message_time": message.timestamp.isoformat(),
                "total_messages": str(len(session.messages) if session else 1),
            },
        )
        await self.redis_client.expire(summary_key, self.ttl)

    async def clear_user_cache(self, user_id: str) -> None:
        """Clear all cache for a user"""
        await self._connect()

        # Get all user-related keys
        patterns = [
            f"user:{user_id}:properties:*",
            f"user:{user_id}:sessions",
            f"session:{user_id}:*:summary",
        ]

        for pattern in patterns:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
