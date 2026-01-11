from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Workspace, WorkspaceMember, User


class CRUDWorkspace:
    async def get(self, db: AsyncSession, id: int) -> Optional[Workspace]:
        result = await db.execute(select(Workspace).filter(Workspace.id == id))
        return result.scalars().first()

    async def get_multi_by_user(
        self, db: AsyncSession, user_id: int
    ) -> List[Workspace]:
        # Get workspaces where user is owner or member
        query = (
            select(Workspace)
            .join(
                WorkspaceMember,
                Workspace.id == WorkspaceMember.workspace_id,
                isouter=True,
            )
            .filter(
                (Workspace.owner_id == user_id) | (WorkspaceMember.user_id == user_id)
            )
            .distinct()
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: dict, owner_id: int) -> Workspace:
        obj_in["owner_id"] = owner_id
        db_obj = Workspace(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Add owner as admin member
        member = WorkspaceMember(workspace_id=db_obj.id, user_id=owner_id, role="owner")
        db.add(member)
        await db.commit()

        return db_obj

    async def add_member(
        self, db: AsyncSession, workspace_id: int, user_id: int, role: str
    ) -> WorkspaceMember:
        member = WorkspaceMember(workspace_id=workspace_id, user_id=user_id, role=role)
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member


workspace = CRUDWorkspace()
