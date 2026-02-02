"""Health entry_type + extra metrics; Learning courses + source_type; Productivity tasks + focus_category + focus_sessions

Revision ID: 0007_extensions
Revises: 0006_add_archived_to_user_goals
Create Date: 2026-01-30

"""

from alembic import op
import sqlalchemy as sa


revision = "0007_extensions"
down_revision = "0006_add_archived_to_user_goals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Health: multiple entries per day + extra metrics ---
    op.add_column(
        "health_entries",
        sa.Column("entry_type", sa.String(32), nullable=False, server_default="day"),
    )
    op.add_column(
        "health_entries",
        sa.Column("steps", sa.Integer(), nullable=True),
    )
    op.add_column(
        "health_entries",
        sa.Column("heart_rate_avg", sa.Integer(), nullable=True),
    )
    op.add_column(
        "health_entries",
        sa.Column("workout_minutes", sa.Integer(), nullable=True),
    )

    # --- Learning: courses/topics ---
    op.create_table(
        "learning_courses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("kind", sa.String(32), nullable=True),  # course, book, topic
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_learning_courses_user_id", "learning_courses", ["user_id"])

    op.add_column(
        "learning_entries",
        sa.Column("course_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "learning_entries",
        sa.Column("source_type", sa.String(32), nullable=True),  # book, course, podcast
    )
    op.create_foreign_key(
        "fk_learning_entries_course",
        "learning_entries",
        "learning_courses",
        ["course_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # --- Productivity: tasks ---
    op.create_table(
        "productivity_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="open"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_productivity_tasks_user_id", "productivity_tasks", ["user_id"])
    op.create_index("ix_productivity_tasks_status", "productivity_tasks", ["status"])

    op.add_column(
        "productivity_entries",
        sa.Column("focus_category", sa.String(64), nullable=True),  # code, writing, meetings
    )

    # --- Productivity: focus sessions (Pomodoro/timers) ---
    op.create_table(
        "focus_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("session_type", sa.String(32), nullable=True),  # pomodoro, deep_work
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_focus_sessions_user_id", "focus_sessions", ["user_id"])
    op.create_index("ix_focus_sessions_local_date", "focus_sessions", ["local_date"])


def downgrade() -> None:
    op.drop_index("ix_focus_sessions_local_date", "focus_sessions")
    op.drop_index("ix_focus_sessions_user_id", "focus_sessions")
    op.drop_table("focus_sessions")

    op.drop_column("productivity_entries", "focus_category")

    op.drop_index("ix_productivity_tasks_status", "productivity_tasks")
    op.drop_index("ix_productivity_tasks_user_id", "productivity_tasks")
    op.drop_table("productivity_tasks")

    op.drop_constraint("fk_learning_entries_course", "learning_entries", type_="foreignkey")
    op.drop_column("learning_entries", "source_type")
    op.drop_column("learning_entries", "course_id")

    op.drop_index("ix_learning_courses_user_id", "learning_courses")
    op.drop_table("learning_courses")

    op.drop_column("health_entries", "workout_minutes")
    op.drop_column("health_entries", "heart_rate_avg")
    op.drop_column("health_entries", "steps")
    op.drop_column("health_entries", "entry_type")
