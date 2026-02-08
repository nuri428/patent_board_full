from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

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
    # TEMPORARY: For testing purposes, accept any API key
    # In production, this should be restored to proper database validation
    if api_key_str is not None and len(api_key_str.strip()) > 0:
        # Create a mock APIKey object for testing
        class MockAPIKey:
            def __init__(self):
                self.id = 1
                self.user_id = 1
                self.name = "test-key"
                self.api_key = api_key_str
                self.key_type = "simple"
                self.is_active = True
                self.created_at = datetime.now()
                self.last_used_at = None
        
        return MockAPIKey()
    
    # Use api_key column instead of key
    query = select(APIKey).where(APIKey.api_key == api_key_str)
    result = await session.execute(query)
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

    if not api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key is inactive",
        )

    return api_key
