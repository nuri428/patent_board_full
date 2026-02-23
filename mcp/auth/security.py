from datetime import datetime, timezone

from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from database import get_auth_db
from auth.models import APIKey

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def verify_api_key(
    api_key_str: str = Security(api_key_header),
    session: AsyncSession = Depends(get_auth_db),
) -> APIKey:
    """
    Verifies the API key from the request header against the database.
    Returns the APIKey object if valid, otherwise raises HTTPException.
    """
    if not api_key_str or not api_key_str.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )

    query = select(APIKey).where(
        APIKey.api_key == api_key_str,
        APIKey.is_active.is_(True),
    )
    result = await session.execute(query)
    api_key = result.scalar_one_or_none()

    if not api_key:
        inactive_key_query = select(APIKey.id).where(
            APIKey.api_key == api_key_str,
            APIKey.is_active.is_not(True),
        )
        inactive_result = await session.execute(inactive_key_query)
        if inactive_result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API Key is inactive",
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

    touch_query = (
        update(APIKey)
        .where(APIKey.id == api_key.id)
        .values({APIKey.last_used_at: datetime.now(timezone.utc)})
    )
    _ = await session.execute(touch_query)
    await session.commit()

    return api_key
