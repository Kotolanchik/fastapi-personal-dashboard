from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class DimDate(Base):
    __tablename__ = "dim_date"

    date_id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)


class DimUser(Base):
    __tablename__ = "dim_user"

    user_id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    role = Column(String(32), nullable=False, default="user")


class FactHealth(Base):
    __tablename__ = "fact_health"
    __table_args__ = (
        UniqueConstraint("user_id", "source_entry_id", name="uq_fact_health_entry"),
    )

    id = Column(Integer, primary_key=True)
    source_entry_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("dim_user.user_id"), nullable=False, index=True)
    date_id = Column(Integer, ForeignKey("dim_date.date_id"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    sleep_hours = Column(Float, nullable=False)
    energy_level = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=True)
    wellbeing = Column(Integer, nullable=False)
    loaded_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("DimUser")
    date = relationship("DimDate")


class FactFinance(Base):
    __tablename__ = "fact_finance"
    __table_args__ = (
        UniqueConstraint("user_id", "source_entry_id", name="uq_fact_finance_entry"),
    )

    id = Column(Integer, primary_key=True)
    source_entry_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("dim_user.user_id"), nullable=False, index=True)
    date_id = Column(Integer, ForeignKey("dim_date.date_id"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    income = Column(Float, nullable=False)
    expense_food = Column(Float, nullable=False)
    expense_transport = Column(Float, nullable=False)
    expense_health = Column(Float, nullable=False)
    expense_other = Column(Float, nullable=False)
    loaded_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("DimUser")
    date = relationship("DimDate")


class FactProductivity(Base):
    __tablename__ = "fact_productivity"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "source_entry_id", name="uq_fact_productivity_entry"
        ),
    )

    id = Column(Integer, primary_key=True)
    source_entry_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("dim_user.user_id"), nullable=False, index=True)
    date_id = Column(Integer, ForeignKey("dim_date.date_id"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    deep_work_hours = Column(Float, nullable=False)
    tasks_completed = Column(Integer, nullable=False)
    focus_level = Column(Integer, nullable=False)
    loaded_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("DimUser")
    date = relationship("DimDate")


class FactLearning(Base):
    __tablename__ = "fact_learning"
    __table_args__ = (
        UniqueConstraint("user_id", "source_entry_id", name="uq_fact_learning_entry"),
    )

    id = Column(Integer, primary_key=True)
    source_entry_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("dim_user.user_id"), nullable=False, index=True)
    date_id = Column(Integer, ForeignKey("dim_date.date_id"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    study_hours = Column(Float, nullable=False)
    loaded_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("DimUser")
    date = relationship("DimDate")
