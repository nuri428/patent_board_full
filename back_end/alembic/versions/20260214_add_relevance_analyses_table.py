"""Add relevance_analyses table

Revision ID: 20260214_add_relevance_analyses
Revises: 20260214_add_session_favorites
Create Date: 2026-02-14 22:40:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260214_add_relevance_analyses"
down_revision: str | Sequence[str] | None = "20260214_add_session_favorites"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "relevance_analyses",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("session_id", sa.String(36), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("analysis_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        mysql_engine="InnoDB",
    )

    op.create_index(
        op.f("ix_relevance_analyses_session_id"), "relevance_analyses", ["session_id"]
    )
    op.create_index(
        op.f("ix_relevance_analyses_user_id"), "relevance_analyses", ["user_id"]
    )
    op.create_index(
        op.f("ix_relevance_analyses_relevance_score"),
        "relevance_analyses",
        ["relevance_score"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_relevance_analyses_relevance_score"), table_name="relevance_analyses"
    )
    op.drop_index(op.f("ix_relevance_analyses_user_id"), table_name="relevance_analyses")
    op.drop_index(
        op.f("ix_relevance_analyses_session_id"), table_name="relevance_analyses"
    )
    op.drop_table("relevance_analyses")
