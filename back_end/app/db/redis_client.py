import redis.asyncio as aioredis
import json
import logging
from typing import Optional, Dict, List
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for session management with connection pooling and retry logic"""

    def __init__(self):
        """Initialize Redis connection pool with retry logic"""
        self.redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
        )

    async def ping(self) -> bool:
        """Check Redis connection"""
        try:
            return await self.redis.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    async def set_session(self, session_id: str, data: Dict, ttl: int = 1800) -> bool:
        """Store session in Redis with TTL (default 30 minutes)"""
        key = f"session:{session_id}"
        try:
            await self.redis.setex(key, ttl, json.dumps(data))
            return True
        except ConnectionError as e:
            logger.error(f"Failed to set session due to connection error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis unavailable - session storage failed"
            )
        except Exception as e:
            logger.error(f"Failed to set session: {e}")
            return False

    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session from Redis"""
        key = f"session:{session_id}"
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except ConnectionError as e:
            logger.error(f"Failed to get session due to connection error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis unavailable - session retrieval failed"
            )
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None

    async def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis"""
        key = f"session:{session_id}"
        try:
            await self.redis.delete(key)
            return True
        except ConnectionError as e:
            logger.error(f"Failed to delete session due to connection error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis unavailable - session deletion failed"
            )
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False

    async def list_user_sessions(self, user_id: int) -> List[str]:
        """List all session IDs for a user"""
        pattern = f"session:*"
        try:
            keys = await self.redis.keys(pattern)
            user_sessions = []
            for key in keys:
                data = await self.redis.get(key)
                if data:
                    try:
                        session = json.loads(data)
                        if session.get("user_id") == user_id:
                            session_id = key.replace("session:", "")
                            user_sessions.append(session_id)
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"Failed to parse session data for key: {key}")
            return user_sessions
        except ConnectionError as e:
            logger.error(f"Failed to list sessions due to connection error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis unavailable - session listing failed"
            )
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []

    async def update_session(self, session_id: str, data: Dict) -> bool:
        """Update session in Redis"""
        return await self.set_session(session_id, data)

    async def acquire_lock(self, session_id: str, timeout: int = 30) -> bool:
        """Acquire session lock using SET NX EX pattern"""
        lock_key = f"lock:session:{session_id}"
        try:
            # SET NX EX - set if not exists with expiration
            return await self.redis.set(lock_key, "locked", nx=True, ex=timeout)
        except ConnectionError as e:
            logger.error(f"Failed to acquire lock due to connection error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis unavailable - lock acquisition failed"
            )
        except Exception as e:
            logger.error(f"Failed to acquire lock: {e}")
            return False

    async def release_lock(self, session_id: str) -> bool:
        """Release session lock"""
        lock_key = f"lock:session:{session_id}"
        try:
            await self.redis.delete(lock_key)
            return True
        except ConnectionError as e:
            logger.error(f"Failed to release lock due to connection error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis unavailable - lock release failed"
            )
        except Exception as e:
            logger.error(f"Failed to release lock: {e}")
            return False

    async def close(self):
        """Close Redis connection"""
        try:
            await self.redis.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")


# Global instance
redis_client = RedisClient()


async def get_redis():
    """Dependency injection for Redis client"""
    return redis_client
