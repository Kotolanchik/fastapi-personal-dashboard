"""add default_timezone to users

Revision ID: 0004_add_default_timezone_to_users
Revises: 0003_add_integrations_and_billing
Create Date: 2026-01-30

"""

from alembic import op
import sqlalchemy as sa


revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("default_timezone", sa.String(length=64), nullable=True, server_default="UTC"),
    )


def downgrade() -> None:
    op.drop_column("users", "default_timezone")
