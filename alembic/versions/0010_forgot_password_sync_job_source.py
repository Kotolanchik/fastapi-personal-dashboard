"""Forgot password (users) + SyncJob.data_source_id

Revision ID: 0010_forgot_password_sync
Revises: 0009_integrations
Create Date: 2026-01-30

"""

from alembic import op
import sqlalchemy as sa


revision = "0010_forgot_password_sync"
down_revision = "0009_integrations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_reset_token", sa.String(255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("password_reset_expires", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_password_reset_token", "users", ["password_reset_token"], unique=False)

    op.add_column(
        "sync_jobs",
        sa.Column("data_source_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_sync_jobs_data_source",
        "sync_jobs",
        "data_sources",
        ["data_source_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_sync_jobs_data_source_id", "sync_jobs", ["data_source_id"])


def downgrade() -> None:
    op.drop_index("ix_sync_jobs_data_source_id", "sync_jobs")
    op.drop_constraint("fk_sync_jobs_data_source", "sync_jobs", type_="foreignkey")
    op.drop_column("sync_jobs", "data_source_id")

    op.drop_index("ix_users_password_reset_token", "users")
    op.drop_column("users", "password_reset_expires")
    op.drop_column("users", "password_reset_token")
