from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List
from app.models import Notification
from app.schemas import NotificationCreate
from datetime import datetime


class NotificationCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_user_notifications(
        self, user_id: int, unread_only: bool = False, skip: int = 0, limit: int = 50
    ) -> List[Notification]:
        """Get user notifications"""
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.is_read == False)

        query = query.order_by(desc(Notification.created_at))
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, notification_create: NotificationCreate) -> Notification:
        """Create new notification"""
        db_notification = Notification(
            user_id=notification_create.user_id,
            title=notification_create.title,
            message=notification_create.message,
            notification_type=notification_create.notification_type,
        )

        self.db.add(db_notification)
        await self.db.commit()
        await self.db.refresh(db_notification)
        return db_notification

    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read"""
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id, Notification.user_id == user_id
            )
        )
        notification = result.scalar_one_or_none()

        if not notification:
            return False

        notification.is_read = True
        notification.read_at = datetime.utcnow()

        await self.db.commit()
        return True

    async def mark_all_as_read(self, user_id: int) -> int:
        """Mark all user notifications as read"""
        from sqlalchemy import update

        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True, read_at=datetime.utcnow())
        )

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def delete(self, notification_id: int, user_id: int) -> bool:
        """Delete notification"""
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id, Notification.user_id == user_id
            )
        )
        notification = result.scalar_one_or_none()

        if not notification:
            return False

        await self.db.delete(notification)
        await self.db.commit()
        return True

    async def get_unread_count(self, user_id: int) -> int:
        """Get unread notification count for user"""
        result = await self.db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id, Notification.is_read == False
            )
        )
        return result.scalar()


# Helper function to get notification CRUD instance
def get_notification_crud(db: AsyncSession) -> NotificationCRUD:
    return NotificationCRUD(db)
