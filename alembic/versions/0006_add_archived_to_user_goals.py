"""add archived to user_goals

Revision ID: 0006_add_archived_to_user_goals
Revises: 0005_add_user_goals
Create Date: 2026-01-30

"""

from alembic import op
import sqlalchemy as sa


revision = "0006_add_archived_to_user_goals"
down_revision = "0005_add_user_goals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_goals",
        sa.Column("archived", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("user_goals", "archived")
