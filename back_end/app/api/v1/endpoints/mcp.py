from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db
from app.api import deps
from app.models import User
from app.schemas.mcp import MCPKeyCreate, MCPKeyRead, MCPKeyResult
from app.crud.mcp import get_mcp_crud

router = APIRouter()


@router.get("/keys", response_model=List[MCPKeyRead])
async def list_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List all MCP API keys for current user.
    """
    crud = get_mcp_crud(db)
    keys = await crud.get_by_user(user_id=current_user.id)
    return keys


@router.post("/keys", response_model=MCPKeyResult)
async def generate_key(
    key_in: MCPKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a new MCP API key.
    """
    crud = get_mcp_crud(db)
    key = await crud.create(key_in=key_in, user_id=current_user.id)
    return key


@router.delete("/keys/{key_id}", response_model=bool)
async def revoke_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Revoke an MCP API key.
    """
    crud = get_mcp_crud(db)
    result = await crud.revoke(key_id=key_id, user_id=current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Key not found")
    return True
