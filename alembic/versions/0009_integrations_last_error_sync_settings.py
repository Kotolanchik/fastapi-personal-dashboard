"""DataSource: last_error, sync_settings for integrations

Revision ID: 0009_integrations
Revises: 0008_entry_completed_tasks
Create Date: 2026-01-30

"""

from alembic import op
import sqlalchemy as sa


revision = "0009_integrations"
down_revision = "0008_entry_completed_tasks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "data_sources",
        sa.Column("last_error", sa.String(512), nullable=True),
    )
    op.add_column(
        "data_sources",
        sa.Column("sync_settings", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("data_sources", "sync_settings")
    op.drop_column("data_sources", "last_error")
