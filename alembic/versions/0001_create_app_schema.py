"""create app schema

Revision ID: 0001_create_app_schema
Revises:
Create Date: 2026-01-30 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_create_app_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"])

    op.create_table(
        "health_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("sleep_hours", sa.Float(), nullable=False),
        sa.Column("energy_level", sa.Integer(), nullable=False),
        sa.Column("supplements", sa.String(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("wellbeing", sa.Integer(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_health_entries_id", "health_entries", ["id"])
    op.create_index("ix_health_entries_local_date", "health_entries", ["local_date"])
    op.create_index("ix_health_entries_user_id", "health_entries", ["user_id"])

    op.create_table(
        "finance_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("income", sa.Float(), nullable=False),
        sa.Column("expense_food", sa.Float(), nullable=False),
        sa.Column("expense_transport", sa.Float(), nullable=False),
        sa.Column("expense_health", sa.Float(), nullable=False),
        sa.Column("expense_other", sa.Float(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_finance_entries_id", "finance_entries", ["id"])
    op.create_index("ix_finance_entries_local_date", "finance_entries", ["local_date"])
    op.create_index("ix_finance_entries_user_id", "finance_entries", ["user_id"])

    op.create_table(
        "productivity_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("deep_work_hours", sa.Float(), nullable=False),
        sa.Column("tasks_completed", sa.Integer(), nullable=False),
        sa.Column("focus_level", sa.Integer(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_productivity_entries_id", "productivity_entries", ["id"])
    op.create_index(
        "ix_productivity_entries_local_date",
        "productivity_entries",
        ["local_date"],
    )
    op.create_index("ix_productivity_entries_user_id", "productivity_entries", ["user_id"])

    op.create_table(
        "learning_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("study_hours", sa.Float(), nullable=False),
        sa.Column("topics", sa.String(), nullable=True),
        sa.Column("projects", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_learning_entries_id", "learning_entries", ["id"])
    op.create_index("ix_learning_entries_local_date", "learning_entries", ["local_date"])
    op.create_index("ix_learning_entries_user_id", "learning_entries", ["user_id"])


def downgrade() -> None:
    op.drop_table("learning_entries")
    op.drop_table("productivity_entries")
    op.drop_table("finance_entries")
    op.drop_table("health_entries")
    op.drop_table("users")
