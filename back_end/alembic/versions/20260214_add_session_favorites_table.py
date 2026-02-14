"""Add session_favorites table

Revision ID: 20260214_add_session_favorites
Revises: a7b3c5d8e2f4, 0002_add_patent_analyses_table
Create Date: 2026-02-14 21:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260214_add_session_favorites"
down_revision: Union[str, Sequence[str], None] = (
    "a7b3c5d8e2f4",
    "0002_add_patent_analyses_table",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "session_favorites",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("session_id", sa.String(36), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("keywords", sa.JSON(), nullable=True),
        sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        mysql_engine="InnoDB",
    )

    op.create_index(op.f("ix_session_favorites_user_id"), "session_favorites", ["user_id"])
    op.create_index(
        op.f("ix_session_favorites_session_id"), "session_favorites", ["session_id"]
    )
    op.create_index(
        op.f("ix_session_favorites_is_pinned"), "session_favorites", ["is_pinned"]
    )
    op.create_index(
        "idx_session_favorites_user_session",
        "session_favorites",
        ["user_id", "session_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("idx_session_favorites_user_session", table_name="session_favorites")
    op.drop_index(op.f("ix_session_favorites_is_pinned"), table_name="session_favorites")
    op.drop_index(op.f("ix_session_favorites_session_id"), table_name="session_favorites")
    op.drop_index(op.f("ix_session_favorites_user_id"), table_name="session_favorites")
    op.drop_table("session_favorites")
