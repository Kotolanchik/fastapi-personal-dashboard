"""Link productivity entries to completed tasks (tasks_completed <-> real tasks)

Revision ID: 0008_entry_completed_tasks
Revises: 0007_extensions
Create Date: 2026-01-30

"""

from alembic import op
import sqlalchemy as sa


revision = "0008_entry_completed_tasks"
down_revision = "0007_extensions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "productivity_entry_completed_tasks",
        sa.Column("entry_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["entry_id"], ["productivity_entries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["productivity_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("entry_id", "task_id"),
    )
    op.create_index(
        "ix_productivity_entry_completed_tasks_entry_id",
        "productivity_entry_completed_tasks",
        ["entry_id"],
    )
    op.create_index(
        "ix_productivity_entry_completed_tasks_task_id",
        "productivity_entry_completed_tasks",
        ["task_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_productivity_entry_completed_tasks_task_id", "productivity_entry_completed_tasks")
    op.drop_index("ix_productivity_entry_completed_tasks_entry_id", "productivity_entry_completed_tasks")
    op.drop_table("productivity_entry_completed_tasks")
