from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, cast

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config.settings import settings
from database import get_auth_db
from auth.models import APIKey

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_auth = HTTPBearer(auto_error=False)


async def _validate_db_api_key(
    api_key_str: str,
    session: AsyncSession,
) -> Any:
    query = select(APIKey).where(APIKey.api_key == api_key_str)
    result = await session.execute(query)
    api_key = result.scalar_one_or_none()

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

    api_key_obj = cast(Any, api_key)

    if api_key_obj.is_active is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key is inactive",
        )

    return api_key_obj


def _validate_jwt_token(token: str) -> SimpleNamespace:
    jwt_secret = getattr(settings, "MCP_JWT_SECRET_KEY", None)
    jwt_algorithm = getattr(settings, "MCP_JWT_ALGORITHM", "HS256")
    if not jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT authentication is not configured",
        )
    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=[jwt_algorithm],
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        ) from exc

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT subject is required",
        )

    return SimpleNamespace(
        id=payload.get("jti") or subject,
        user_id=payload.get("user_id") or subject,
        name=payload.get("name") or f"jwt:{subject}",
        api_key="<jwt>",
        key_type="jwt",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        last_used_at=datetime.now(timezone.utc),
        claims=payload,
    )


async def verify_api_key(
    api_key_str: str | None = Security(api_key_header),
    bearer_credentials: HTTPAuthorizationCredentials | None = Security(bearer_auth),
    session: AsyncSession = Depends(get_auth_db),
) -> Any:
    """
    Verifies the API key from the request header against the database.
    Returns the APIKey object if valid, otherwise raises HTTPException.
    """
    if api_key_str:
        cleaned_key = api_key_str.strip()
        if cleaned_key:
            if (
                getattr(settings, "MCP_ALLOW_MASTER_KEY", True)
                and settings.MCP_API_KEY
                and cleaned_key == settings.MCP_API_KEY
            ):
                return SimpleNamespace(
                    id="master",
                    user_id=0,
                    name="master-key",
                    api_key=cleaned_key,
                    key_type="master",
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                    last_used_at=datetime.now(timezone.utc),
                )

            if getattr(settings, "MCP_AUTH_ALLOW_NON_DB_KEYS", False):
                return SimpleNamespace(
                    id="non-db",
                    user_id=0,
                    name="non-db-key",
                    api_key=cleaned_key,
                    key_type="development",
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                    last_used_at=datetime.now(timezone.utc),
                )

            return await _validate_db_api_key(cleaned_key, session)

    if bearer_credentials and bearer_credentials.credentials:
        return _validate_jwt_token(bearer_credentials.credentials)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required via X-API-Key or Bearer token",
    )
