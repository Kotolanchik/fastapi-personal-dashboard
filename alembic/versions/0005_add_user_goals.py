"""add user_goals table

Revision ID: 0005_add_user_goals
Revises: 0004_add_default_timezone_to_users
Create Date: 2026-01-30

"""

from alembic import op
import sqlalchemy as sa


revision = "0005_add_user_goals"
down_revision = "0004_add_default_timezone_to_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_goals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("sphere", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=True),
        sa.Column("target_metric", sa.String(length=64), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_user_goals_id", "user_goals", ["id"])
    op.create_index("ix_user_goals_user_id", "user_goals", ["user_id"])


def downgrade() -> None:
    op.drop_table("user_goals")
