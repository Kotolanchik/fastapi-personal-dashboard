from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class TimestampMixin:
    id = Column(Integer, primary_key=True, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    local_date = Column(Date, nullable=False, index=True)
    timezone = Column(String(64), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    role = Column(String(32), nullable=False, default="user")

    health_entries = relationship("HealthEntry", back_populates="user")
    finance_entries = relationship("FinanceEntry", back_populates="user")
    productivity_entries = relationship("ProductivityEntry", back_populates="user")
    learning_entries = relationship("LearningEntry", back_populates="user")


class HealthEntry(Base, TimestampMixin):
    __tablename__ = "health_entries"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sleep_hours = Column(Float, nullable=False)
    energy_level = Column(Integer, nullable=False)
    supplements = Column(String, nullable=True)
    weight_kg = Column(Float, nullable=True)
    wellbeing = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)

    user = relationship("User", back_populates="health_entries")


class FinanceEntry(Base, TimestampMixin):
    __tablename__ = "finance_entries"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    income = Column(Float, nullable=False)
    expense_food = Column(Float, nullable=False)
    expense_transport = Column(Float, nullable=False)
    expense_health = Column(Float, nullable=False)
    expense_other = Column(Float, nullable=False)
    notes = Column(String, nullable=True)

    user = relationship("User", back_populates="finance_entries")


class ProductivityEntry(Base, TimestampMixin):
    __tablename__ = "productivity_entries"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    deep_work_hours = Column(Float, nullable=False)
    tasks_completed = Column(Integer, nullable=False)
    focus_level = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)

    user = relationship("User", back_populates="productivity_entries")


class LearningEntry(Base, TimestampMixin):
    __tablename__ = "learning_entries"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    study_hours = Column(Float, nullable=False)
    topics = Column(String, nullable=True)
    projects = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    user = relationship("User", back_populates="learning_entries")
