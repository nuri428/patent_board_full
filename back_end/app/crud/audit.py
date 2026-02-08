from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog
from typing import Optional, Any, Dict


class AuditCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        payload: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        db_obj = AuditLog(
            action=action,
            user_id=user_id,
            username=username,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            payload=payload,
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj


def get_audit_crud(db: AsyncSession) -> AuditCRUD:
    return AuditCRUD(db)
