from fastapi import APIRouter, HTTPException, status
from app.db.redis_client import redis_client

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/redis")
async def redis_health():
    """Redis health check endpoint"""
    if await redis_client.ping():
        return {"status": "ok"}
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Redis unavailable"
    )
