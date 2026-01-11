from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db
from app.crud.prompt_template import prompt_template as prompt_crud
from app.models import User
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[dict])
async def read_prompt_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve prompt templates.
    """
    prompts = await prompt_crud.get_multi(db, skip=skip, limit=limit)
    return prompts


@router.post("/", response_model=dict)
async def create_prompt_template(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
    name: str,
    template: str,
    description: str = None,
    report_type: str = None,
) -> Any:
    """
    Create new prompt template (Admin only).
    """
    prompt = await prompt_crud.create(
        db,
        obj_in={
            "name": name,
            "template": template,
            "description": description,
            "report_type": report_type,
        },
    )
    return prompt
