from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models import User, Report, ChatSession, Notification
from app.schemas import UserCreate, UserUpdate
import bcrypt

# Monkeypatch bcrypt for passlib compatibility (if needed)
try:
    if not hasattr(bcrypt, "__about__"):

        class About:
            __version__ = getattr(bcrypt, "__version__", "unknown")

        bcrypt.__about__ = About()
except Exception:
    pass


# Monkeypatch bcrypt.hashpw to truncate passwords to 71 bytes (avoid 72-byte limit)
_original_hashpw = bcrypt.hashpw


def _patched_hashpw(password, salt):
    if isinstance(password, str):
        password = password.encode('utf-8')
    if len(password) > 71:
        password = password[:71]
    return _original_hashpw(password, salt)


bcrypt.hashpw = _patched_hashpw


# Monkeypatch passlib's detect_wrap_bug to avoid RuntimeError on startup
import passlib.handlers.bcrypt


def _patched_detect_wrap_bug(ident):
    return False


passlib.handlers.bcrypt.detect_wrap_bug = _patched_detect_wrap_bug


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[User]:
        """Get multiple users with pagination"""
        query = select(User)
        if active_only:
            query = query.where(User.is_active == True)
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, user_create: UserCreate) -> User:
        """Create new user"""
        hashed_password = pwd_context.hash(user_create.password)

        db_user = User(
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
            is_active=user_create.is_active,
            role=getattr(user_create, "role", "analyst"),
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def update(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user"""
        db_user = await self.get(user_id)
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = pwd_context.hash(
                update_data.pop("password")
            )

        for field, value in update_data.items():
            setattr(db_user, field, value)

        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def delete(self, user_id: int) -> bool:
        """Delete user (soft delete by setting is_active=False)"""
        db_user = await self.get(user_id)
        if not db_user:
            return False

        db_user.is_active = False
        await self.db.commit()
        return True

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = await self.get_by_email(email)
        if not user or not user.is_active:
            return None

        if not pwd_context.verify(password, user.hashed_password):
            return None

        return user

    async def get_user_reports(self, user_id: int) -> List[Report]:
        """Get all reports for a user"""
        result = await self.db.execute(
            select(Report)
            .where(Report.owner_id == user_id)
            .order_by(Report.created_at.desc())
        )
        return result.scalars().all()

    async def get_user_sessions(self, user_id: int) -> List[ChatSession]:
        """Get all chat sessions for a user"""
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
        )
        return result.scalars().all()

    async def get_user_notifications(
        self, user_id: int, unread_only: bool = False
    ) -> List[Notification]:
        """Get user notifications"""
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.is_read == False)

        query = query.order_by(Notification.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()


# Helper function to get user CRUD instance
def get_user_crud(db: AsyncSession) -> UserCRUD:
    return UserCRUD(db)
