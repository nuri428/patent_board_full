from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db
from app.crud.workspace import workspace as workspace_crud
from app.models import User
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[dict])
async def read_workspaces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve workspaces.
    """
    workspaces = await workspace_crud.get_multi_by_user(db, user_id=current_user.id)
    return workspaces


@router.post("/", response_model=dict)
async def create_workspace(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    name: str,
) -> Any:
    """
    Create new workspace.
    """
    workspace = await workspace_crud.create(
        db, obj_in={"name": name}, owner_id=current_user.id
    )
    return workspace


@router.post("/{workspace_id}/members", response_model=dict)
async def add_workspace_member(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    workspace_id: int,
    user_id: int,
    role: str = "viewer",
) -> Any:
    """
    Add member to workspace.
    """
    workspace = await workspace_crud.get(db, id=workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if workspace.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    member = await workspace_crud.add_member(
        db, workspace_id=workspace_id, user_id=user_id, role=role
    )
    return member
