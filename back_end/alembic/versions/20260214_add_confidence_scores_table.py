"""Add confidence_scores table

Revision ID: 20260214_add_confidence_scores
Revises: 20260214_add_relevance_analyses
Create Date: 2026-02-14 23:30:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260214_add_confidence_scores"
down_revision: str | Sequence[str] | None = "20260214_add_relevance_analyses"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "confidence_scores",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("session_id", sa.String(36), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("confidence_value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("confidence_level", sa.String(20), nullable=False),
        sa.Column("source_factors", sa.JSON(), nullable=True),
        sa.Column("calculated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        mysql_engine="InnoDB",
    )

    op.create_index(
        op.f("ix_confidence_scores_session_id"), "confidence_scores", ["session_id"]
    )
    op.create_index(op.f("ix_confidence_scores_user_id"), "confidence_scores", ["user_id"])
    op.create_index(
        op.f("ix_confidence_scores_confidence_value"),
        "confidence_scores",
        ["confidence_value"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_confidence_scores_confidence_value"), table_name="confidence_scores"
    )
    op.drop_index(op.f("ix_confidence_scores_user_id"), table_name="confidence_scores")
    op.drop_index(op.f("ix_confidence_scores_session_id"), table_name="confidence_scores")
    op.drop_table("confidence_scores")
