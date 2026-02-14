"""
Session Groups API Endpoints

Provides REST API endpoints for managing session groups, group members, and tags.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.api.deps import get_current_user
from app.models import User
from app.models.session_group import SessionGroup, GroupMember, SessionGroupTag
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db
from app.crud.crud_session_group import get_session_group_crud

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== Request/Response Models ==========

class SessionGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color_code: str = "#57373"
    is_default: bool = False


class SessionGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color_code: Optional[str] = None
    is_default: Optional[bool] = None


class SessionGroupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    color_code: str
    is_default: bool
    creator_user_id: int
    created_at: datetime
    updated_at: Optional[datetime]


class GroupMemberResponse(BaseModel):
    id: int
    group_id: str
    user_id: int
    role: str
    joined_at: datetime


class TagCreate(BaseModel):
    group_id: str
    name: str
    color_code: Optional[str] = None


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color_code: Optional[str] = None


class TagResponse(BaseModel):
    id: str
    group_id: str
    name: str
    color_code: Optional[str]
    created_at: datetime


class SuccessResponse(BaseModel):
    message: str


# ========== Session Group Endpoints ==========

@router.post("", response_model=SessionGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_session_group(
    group_data: SessionGroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new session group"""
    crud = get_session_group_crud(db)

    try:
        session_group = await crud.create(
            name=group_data.name,
            creator_user_id=current_user.id,
            description=group_data.description,
            color_code=group_data.color_code,
            is_default=group_data.is_default,
        )
        return SessionGroupResponse(
            id=session_group.id,
            name=session_group.name,
            description=session_group.description,
            color_code=session_group.color_code,
            is_default=session_group.is_default,
            creator_user_id=session_group.creator_user_id,
            created_at=session_group.created_at,
            updated_at=session_group.updated_at,
        )
    except Exception as e:
        logger.error(f"Failed to create session group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session group",
        )


@router.get("/{group_id}", response_model=SessionGroupResponse)
async def get_session_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get session group details by ID"""
    crud = get_session_group_crud(db)

    session_group = await crud.get_by_id(group_id)

    if not session_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session group not found",
        )

    # Verify user has access to this group (is a member)
    member = await crud.get_group_member(group_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session group",
        )

    return SessionGroupResponse(
        id=session_group.id,
        name=session_group.name,
        description=session_group.description,
        color_code=session_group.color_code,
        is_default=session_group.is_default,
        creator_user_id=session_group.creator_user_id,
        created_at=session_group.created_at,
        updated_at=session_group.updated_at,
    )


@router.put("/{group_id}", response_model=SessionGroupResponse)
async def update_session_group(
    group_id: str,
    group_update: SessionGroupUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update session group"""
    crud = get_session_group_crud(db)

    # Verify user has access (is member)
    member = await crud.get_group_member(group_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session group",
        )

    # Only owner or admin can update
    if member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or admin can update session group",
        )

    session_group = await crud.update(
        group_id=group_id,
        name=group_update.name,
        description=group_update.description,
        color_code=group_update.color_code,
        is_default=group_update.is_default,
    )

    if not session_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session group not found",
        )

    return SessionGroupResponse(
        id=session_group.id,
        name=session_group.name,
        description=session_group.description,
        color_code=session_group.color_code,
        is_default=session_group.is_default,
        creator_user_id=session_group.creator_user_id,
        created_at=session_group.created_at,
        updated_at=session_group.updated_at,
    )


@router.delete("/{group_id}", response_model=SuccessResponse)
async def delete_session_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a session group"""
    crud = get_session_group_crud(db)

    # Verify user is owner
    member = await crud.get_group_member(group_id, current_user.id)
    if not member or member.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can delete session group",
        )

    success = await crud.delete(group_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session group not found",
        )

    return SuccessResponse(message="Session group deleted successfully")


@router.get("", response_model=List[SessionGroupResponse])
async def list_session_groups(
    name_pattern: Optional[str] = None,
    is_default: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all session groups for current user"""
    crud = get_session_group_crud(db)

    session_groups = await crud.search_groups(
        user_id=current_user.id,
        name_pattern=name_pattern,
        is_default=is_default,
        skip=skip,
        limit=limit,
    )

    return [
        SessionGroupResponse(
            id=g.id,
            name=g.name,
            description=g.description,
            color_code=g.color_code,
            is_default=g.is_default,
            creator_user_id=g.creator_user_id,
            created_at=g.created_at,
            updated_at=g.updated_at,
        )
        for g in session_groups
    ]


@router.get("/user/groups", response_model=List[SessionGroupResponse])
async def list_user_session_groups(
    include_default: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all session groups the user is a member of"""
    crud = get_session_group_crud(db)

    session_groups = await crud.list_user_groups(
        user_id=current_user.id,
        include_default=include_default,
    )

    return [
        SessionGroupResponse(
            id=g.id,
            name=g.name,
            description=g.description,
            color_code=g.color_code,
            is_default=g.is_default,
            creator_user_id=g.creator_user_id,
            created_at=g.created_at,
            updated_at=g.updated_at,
        )
        for g in session_groups
    ]


# ========== Group Member Management Endpoints ==========

@router.post("/{group_id}/members/{user_id}", response_model=GroupMemberResponse)
async def add_user_to_group(
    group_id: str,
    user_id: int,
    role: str = "member",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a user to a session group"""
    crud = get_session_group_crud(db)

    # Verify current user is owner or admin
    member = await crud.get_group_member(group_id, current_user.id)
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or admin can add members to the group",
        )

    # Add user to group
    group_member = await crud.add_user_to_group(
        group_id=group_id,
        user_id=user_id,
        role=role,
    )

    return GroupMemberResponse(
        id=group_member.id,
        group_id=group_member.group_id,
        user_id=group_member.user_id,
        role=group_member.role,
        joined_at=group_member.joined_at,
    )


@router.delete("/{group_id}/members/{user_id}", response_model=SuccessResponse)
async def remove_user_from_group(
    group_id: str,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a user from a session group"""
    crud = get_session_group_crud(db)

    # Verify current user is owner or admin, or is removing themselves
    member = await crud.get_group_member(group_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    if current_user.id != user_id and member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or admin can remove other users",
        )

    success = await crud.remove_user_from_group(group_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group member not found",
        )

    return SuccessResponse(message="User removed from group successfully")


@router.get("/{group_id}/members", response_model=List[GroupMemberResponse])
async def list_group_members(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all members of a session group"""
    crud = get_session_group_crud(db)

    # Verify user has access to this group
    member = await crud.get_group_member(group_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session group",
        )

    members = await crud.list_group_members(group_id)

    return [
        GroupMemberResponse(
            id=m.id,
            group_id=m.group_id,
            user_id=m.user_id,
            role=m.role,
            joined_at=m.joined_at,
        )
        for m in members
    ]


# ========== Tag Management Endpoints ==========

@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a tag for a session group"""
    crud = get_session_group_crud(db)

    # Verify user has access to the group
    member = await crud.get_group_member(tag_data.group_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session group",
        )

    try:
        tag = await crud.create_tag(
            group_id=tag_data.group_id,
            name=tag_data.name,
            color_code=tag_data.color_code,
        )
        return TagResponse(
            id=tag.id,
            group_id=tag.group_id,
            name=tag.name,
            color_code=tag.color_code,
            created_at=tag.created_at,
        )
    except Exception as e:
        logger.error(f"Failed to create tag: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tag",
        )


@router.get("/tags/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get tag details by ID"""
    crud = get_session_group_crud(db)

    tag = await crud.get_tag_by_id(tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    # Verify user has access to the group
    member = await crud.get_group_member(tag.group_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tag",
        )

    return TagResponse(
        id=tag.id,
        group_id=tag.group_id,
        name=tag.name,
        color_code=tag.color_code,
        created_at=tag.created_at,
    )


@router.put("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: str,
    tag_update: TagUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a tag"""
    crud = get_session_group_crud(db)

    # Get tag to check access
    tag = await crud.get_tag_by_id(tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    # Verify user has access to the group
    member = await crud.get_group_member(tag.group_id, current_user.id)
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or admin can update tags",
        )

    updated_tag = await crud.update_tag(
        tag_id=tag_id,
        name=tag_update.name,
        color_code=tag_update.color_code,
    )

    return TagResponse(
        id=updated_tag.id,
        group_id=updated_tag.group_id,
        name=updated_tag.name,
        color_code=updated_tag.color_code,
        created_at=updated_tag.created_at,
    )


@router.delete("/tags/{tag_id}", response_model=SuccessResponse)
async def delete_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a tag"""
    crud = get_session_group_crud(db)

    # Get tag to check access
    tag = await crud.get_tag_by_id(tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    # Verify user has access to the group
    member = await crud.get_group_member(tag.group_id, current_user.id)
    if not member or member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or admin can delete tags",
        )

    success = await crud.delete_tag(tag_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return SuccessResponse(message="Tag deleted successfully")


@router.get("/{group_id}/tags", response_model=List[TagResponse])
async def list_group_tags(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all tags for a session group"""
    crud = get_session_group_crud(db)

    # Verify user has access to the group
    member = await crud.get_group_member(group_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session group",
        )

    tags = await crud.list_group_tags(group_id)

    return [
        TagResponse(
            id=t.id,
            group_id=t.group_id,
            name=t.name,
            color_code=t.color_code,
            created_at=t.created_at,
        )
        for t in tags
    ]
