"""Dashboard widgets, notifications, goals course_complete, expense categories

Revision ID: 0011_dashboard_notif_goals_expense
Revises: 0010_forgot_password_sync
Create Date: 2026-01-30

"""

from alembic import op
import sqlalchemy as sa


revision = "0011_dashboard_notif_goals_expense"
down_revision = "0010_forgot_password_sync"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("dashboard_settings", sa.JSON(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("notification_email", sa.String(255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("notification_preferences", sa.JSON(), nullable=True),
    )

    op.add_column(
        "user_goals",
        sa.Column("course_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_user_goals_course",
        "user_goals",
        "learning_courses",
        ["course_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_user_goals_course_id", "user_goals", ["course_id"])

    op.add_column(
        "learning_courses",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "user_expense_category_mappings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider_category", sa.String(128), nullable=False),
        sa.Column("target_field", sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_expense_category_mappings_user_id",
        "user_expense_category_mappings",
        ["user_id"],
    )
    op.create_index(
        "ix_user_expense_category_mappings_user_provider",
        "user_expense_category_mappings",
        ["user_id", "provider_category"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_user_expense_category_mappings_user_provider",
        "user_expense_category_mappings",
    )
    op.drop_index(
        "ix_user_expense_category_mappings_user_id",
        "user_expense_category_mappings",
    )
    op.drop_table("user_expense_category_mappings")

    op.drop_column("learning_courses", "completed_at")

    op.drop_index("ix_user_goals_course_id", "user_goals")
    op.drop_constraint("fk_user_goals_course", "user_goals", type_="foreignkey")
    op.drop_column("user_goals", "course_id")

    op.drop_column("users", "notification_preferences")
    op.drop_column("users", "notification_email")
    op.drop_column("users", "dashboard_settings")
