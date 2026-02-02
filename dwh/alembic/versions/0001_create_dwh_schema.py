"""create dwh schema

Revision ID: 0001_create_dwh_schema
Revises: 
Create Date: 2026-01-30 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_create_dwh_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dim_date",
        sa.Column("date_id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
    )
    op.create_index("ix_dim_date_date", "dim_date", ["date"], unique=True)

    op.create_table(
        "dim_user",
        sa.Column("user_id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_dim_user_email", "dim_user", ["email"], unique=True)

    op.create_table(
        "fact_health",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_entry_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date_id", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sleep_hours", sa.Float(), nullable=False),
        sa.Column("energy_level", sa.Integer(), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("wellbeing", sa.Integer(), nullable=False),
        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["date_id"], ["dim_date.date_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["dim_user.user_id"]),
        sa.UniqueConstraint("user_id", "source_entry_id", name="uq_fact_health_entry"),
    )
    op.create_index("ix_fact_health_user_id", "fact_health", ["user_id"])
    op.create_index("ix_fact_health_date_id", "fact_health", ["date_id"])

    op.create_table(
        "fact_finance",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_entry_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date_id", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("income", sa.Float(), nullable=False),
        sa.Column("expense_food", sa.Float(), nullable=False),
        sa.Column("expense_transport", sa.Float(), nullable=False),
        sa.Column("expense_health", sa.Float(), nullable=False),
        sa.Column("expense_other", sa.Float(), nullable=False),
        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["date_id"], ["dim_date.date_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["dim_user.user_id"]),
        sa.UniqueConstraint("user_id", "source_entry_id", name="uq_fact_finance_entry"),
    )
    op.create_index("ix_fact_finance_user_id", "fact_finance", ["user_id"])
    op.create_index("ix_fact_finance_date_id", "fact_finance", ["date_id"])

    op.create_table(
        "fact_productivity",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_entry_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date_id", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deep_work_hours", sa.Float(), nullable=False),
        sa.Column("tasks_completed", sa.Integer(), nullable=False),
        sa.Column("focus_level", sa.Integer(), nullable=False),
        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["date_id"], ["dim_date.date_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["dim_user.user_id"]),
        sa.UniqueConstraint("user_id", "source_entry_id", name="uq_fact_productivity_entry"),
    )
    op.create_index("ix_fact_productivity_user_id", "fact_productivity", ["user_id"])
    op.create_index("ix_fact_productivity_date_id", "fact_productivity", ["date_id"])

    op.create_table(
        "fact_learning",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_entry_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date_id", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("study_hours", sa.Float(), nullable=False),
        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["date_id"], ["dim_date.date_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["dim_user.user_id"]),
        sa.UniqueConstraint("user_id", "source_entry_id", name="uq_fact_learning_entry"),
    )
    op.create_index("ix_fact_learning_user_id", "fact_learning", ["user_id"])
    op.create_index("ix_fact_learning_date_id", "fact_learning", ["date_id"])


def downgrade() -> None:
    op.drop_table("fact_learning")
    op.drop_table("fact_productivity")
    op.drop_table("fact_finance")
    op.drop_table("fact_health")
    op.drop_table("dim_user")
    op.drop_table("dim_date")
