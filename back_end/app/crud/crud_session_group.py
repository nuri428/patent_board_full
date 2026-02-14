"""
CRUD operations for Session Groups

Handles database operations for session groups, group members, and tags.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.models.session_group import SessionGroup, GroupMember, SessionGroupTag


class SessionGroupCRUD:
    """CRUD operations for session groups"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== SessionGroup CRUD ==========

    async def create(
        self,
        name: str,
        creator_user_id: int,
        description: Optional[str] = None,
        color_code: str = "#57373",
        is_default: bool = False,
    ) -> SessionGroup:
        """Create a new session group"""
        session_group = SessionGroup(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            color_code=color_code,
            is_default=is_default,
            creator_user_id=creator_user_id,
        )
        self.db.add(session_group)
        await self.db.commit()
        await self.db.refresh(session_group)

        # Add creator as owner
        await self.add_user_to_group(session_group.id, creator_user_id, "owner")

        return session_group

    async def get_by_id(self, group_id: str) -> Optional[SessionGroup]:
        """Get session group by ID"""
        result = await self.db.execute(
            select(SessionGroup).where(SessionGroup.id == group_id)
        )
        return result.scalar_one_or_none()

    async def get_by_creator(
        self, creator_user_id: int, skip: int = 0, limit: int = 100
    ) -> List[SessionGroup]:
        """Get all session groups created by a user"""
        result = await self.db.execute(
            select(SessionGroup)
            .where(SessionGroup.creator_user_id == creator_user_id)
            .order_by(SessionGroup.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update(
        self,
        group_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color_code: Optional[str] = None,
        is_default: Optional[bool] = None,
    ) -> Optional[SessionGroup]:
        """Update session group"""
        db_obj = await self.get_by_id(group_id)
        if db_obj:
            if name is not None:
                db_obj.name = name
            if description is not None:
                db_obj.description = description
            if color_code is not None:
                db_obj.color_code = color_code
            if is_default is not None:
                db_obj.is_default = is_default
            db_obj.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, group_id: str) -> bool:
        """Delete a session group (cascades to members, tags, and sessions)"""
        db_obj = await self.get_by_id(group_id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
            return True
        return False

    # ========== Group Member Management ==========

    async def add_user_to_group(
        self, group_id: str, user_id: int, role: str = "member"
    ) -> GroupMember:
        """Add a user to a group"""
        # Check if user is already in group
        existing = await self.get_group_member(group_id, user_id)
        if existing:
            # Update role if different
            if existing.role != role:
                existing.role = role
                await self.db.commit()
                await self.db.refresh(existing)
            return existing

        # Add new member
        group_member = GroupMember(
            group_id=group_id,
            user_id=user_id,
            role=role,
        )
        self.db.add(group_member)
        await self.db.commit()
        await self.db.refresh(group_member)
        return group_member

    async def remove_user_from_group(self, group_id: str, user_id: int) -> bool:
        """Remove a user from a group"""
        group_member = await self.get_group_member(group_id, user_id)
        if group_member:
            await self.db.delete(group_member)
            await self.db.commit()
            return True
        return False

    async def get_group_member(
        self, group_id: str, user_id: int
    ) -> Optional[GroupMember]:
        """Get group member record"""
        result = await self.db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id, GroupMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_group_members(self, group_id: str) -> List[GroupMember]:
        """List all members of a group"""
        result = await self.db.execute(
            select(GroupMember)
            .where(GroupMember.group_id == group_id)
            .order_by(GroupMember.joined_at.asc())
        )
        return result.scalars().all()

    async def list_user_groups(
        self, user_id: int, include_default: bool = True
    ) -> List[SessionGroup]:
        """List all groups for a user (as a member)"""
        from sqlalchemy import join

        # Join with GroupMember to get groups user is a member of
        result = await self.db.execute(
            select(SessionGroup)
            .join(GroupMember, SessionGroup.id == GroupMember.group_id)
            .where(GroupMember.user_id == user_id)
            .where(SessionGroup.is_default == include_default)  # Filter if requested
            .order_by(SessionGroup.name.asc())
        )
        return result.scalars().all()

    # ========== Tag Management ==========

    async def create_tag(
        self,
        group_id: str,
        name: str,
        color_code: Optional[str] = None,
    ) -> SessionGroupTag:
        """Create a tag for a session group"""
        tag = SessionGroupTag(
            id=str(uuid.uuid4()),
            group_id=group_id,
            name=name,
            color_code=color_code,
        )
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        return tag

    async def get_tag_by_id(self, tag_id: str) -> Optional[SessionGroupTag]:
        """Get tag by ID"""
        result = await self.db.execute(
            select(SessionGroupTag).where(SessionGroupTag.id == tag_id)
        )
        return result.scalar_one_or_none()

    async def update_tag(
        self,
        tag_id: str,
        name: Optional[str] = None,
        color_code: Optional[str] = None,
    ) -> Optional[SessionGroupTag]:
        """Update a tag"""
        db_obj = await self.get_tag_by_id(tag_id)
        if db_obj:
            if name is not None:
                db_obj.name = name
            if color_code is not None:
                db_obj.color_code = color_code
            await self.db.commit()
            await self.db.refresh(db_obj)
        return db_obj

    async def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag"""
        db_obj = await self.get_tag_by_id(tag_id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
            return True
        return False

    async def list_group_tags(self, group_id: str) -> List[SessionGroupTag]:
        """List all tags for a group"""
        result = await self.db.execute(
            select(SessionGroupTag)
            .where(SessionGroupTag.group_id == group_id)
            .order_by(SessionGroupTag.name.asc())
        )
        return result.scalars().all()

    # ========== Search/Query Methods ==========

    async def search_groups(
        self,
        user_id: Optional[int] = None,
        name_pattern: Optional[str] = None,
        is_default: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SessionGroup]:
        """
        Search session groups with filters
        """
        query = select(SessionGroup)

        # Filter by groups user has access to
        if user_id:
            query = query.join(GroupMember, SessionGroup.id == GroupMember.group_id).where(
                GroupMember.user_id == user_id
            )

        # Filter by name pattern
        if name_pattern:
            query = query.where(SessionGroup.name.like(f"%{name_pattern}%"))

        # Filter by default status
        if is_default is not None:
            query = query.where(SessionGroup.is_default == is_default)

        result = await self.db.execute(
            query.order_by(SessionGroup.name.asc()).offset(skip).limit(limit)
        )
        return result.scalars().all()


def get_session_group_crud(db: AsyncSession) -> SessionGroupCRUD:
    """Helper function to get session group CRUD instance"""
    return SessionGroupCRUD(db)
