"""add role to dim_user

Revision ID: 0002_add_role_to_dim_user
Revises: 0001_create_dwh_schema
Create Date: 2026-01-30 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_role_to_dim_user"
down_revision = "0001_create_dwh_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("dim_user", sa.Column("role", sa.String(length=32), nullable=False, server_default="user"))
    op.alter_column("dim_user", "role", server_default=None)


def downgrade() -> None:
    op.drop_column("dim_user", "role")
