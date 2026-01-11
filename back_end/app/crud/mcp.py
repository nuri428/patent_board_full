from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import MCPAPIKey
from app.schemas.mcp import MCPKeyCreate
import secrets
import base64


class MCPKeyCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id: int):
        result = await self.db.execute(
            select(MCPAPIKey)
            .where(MCPAPIKey.user_id == user_id)
            .where(MCPAPIKey.is_active == True)
            .order_by(MCPAPIKey.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, key_in: MCPKeyCreate, user_id: int) -> MCPAPIKey:
        # Generate API Key: pa-apikey-{random}
        random_bytes = secrets.token_bytes(32)
        random_str = base64.urlsafe_b64encode(random_bytes).decode("utf-8").rstrip("=")
        api_key = f"pa-apikey-{random_str}"

        db_key = MCPAPIKey(
            user_id=user_id,
            name=key_in.name,
            key_type=key_in.key_type,
            api_key=api_key,
            is_active=True,
        )
        self.db.add(db_key)
        await self.db.commit()
        await self.db.refresh(db_key)
        return db_key

    async def revoke(self, key_id: int, user_id: int) -> bool:
        result = await self.db.execute(
            select(MCPAPIKey)
            .where(MCPAPIKey.id == key_id)
            .where(MCPAPIKey.user_id == user_id)
        )
        key = result.scalar_one_or_none()
        if key:
            key.is_active = False
            await self.db.commit()
            return True
        return False

    async def get_by_key(self, api_key: str) -> MCPAPIKey | None:
        result = await self.db.execute(
            select(MCPAPIKey)
            .where(MCPAPIKey.api_key == api_key)
            .where(MCPAPIKey.is_active == True)
        )
        return result.scalar_one_or_none()


def get_mcp_crud(db: AsyncSession) -> MCPKeyCRUD:
    return MCPKeyCRUD(db)
