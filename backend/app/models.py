from sqlalchemy import Column, Date, DateTime, Float, Integer, String

from .database import Base


class TimestampMixin:
    id = Column(Integer, primary_key=True, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    local_date = Column(Date, nullable=False, index=True)
    timezone = Column(String(64), nullable=False)


class HealthEntry(Base, TimestampMixin):
    __tablename__ = "health_entries"

    sleep_hours = Column(Float, nullable=False)
    energy_level = Column(Integer, nullable=False)
    supplements = Column(String, nullable=True)
    weight_kg = Column(Float, nullable=True)
    wellbeing = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)


class FinanceEntry(Base, TimestampMixin):
    __tablename__ = "finance_entries"

    income = Column(Float, nullable=False)
    expense_food = Column(Float, nullable=False)
    expense_transport = Column(Float, nullable=False)
    expense_health = Column(Float, nullable=False)
    expense_other = Column(Float, nullable=False)
    notes = Column(String, nullable=True)


class ProductivityEntry(Base, TimestampMixin):
    __tablename__ = "productivity_entries"

    deep_work_hours = Column(Float, nullable=False)
    tasks_completed = Column(Integer, nullable=False)
    focus_level = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)


class LearningEntry(Base, TimestampMixin):
    __tablename__ = "learning_entries"

    study_hours = Column(Float, nullable=False)
    topics = Column(String, nullable=True)
    projects = Column(String, nullable=True)
    notes = Column(String, nullable=True)
