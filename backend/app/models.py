from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
)
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
    default_timezone = Column(String(64), nullable=True, server_default="UTC")
    created_at = Column(DateTime(timezone=True), nullable=False)
    role = Column(String(32), nullable=False, default="user")

    health_entries = relationship("HealthEntry", back_populates="user")
    finance_entries = relationship("FinanceEntry", back_populates="user")
    productivity_entries = relationship("ProductivityEntry", back_populates="user")
    learning_entries = relationship("LearningEntry", back_populates="user")
    learning_courses = relationship("LearningCourse", back_populates="user", cascade="all, delete-orphan")
    productivity_tasks = relationship("ProductivityTask", back_populates="user", cascade="all, delete-orphan")
    focus_sessions = relationship("FocusSession", back_populates="user", cascade="all, delete-orphan")
    data_sources = relationship("DataSource", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    goals = relationship("UserGoal", back_populates="user", cascade="all, delete-orphan")


class HealthEntry(Base, TimestampMixin):
    __tablename__ = "health_entries"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    entry_type = Column(String(32), nullable=False, default="day")  # day, morning, evening
    sleep_hours = Column(Float, nullable=False)
    energy_level = Column(Integer, nullable=False)
    supplements = Column(String, nullable=True)
    weight_kg = Column(Float, nullable=True)
    wellbeing = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)
    steps = Column(Integer, nullable=True)
    heart_rate_avg = Column(Integer, nullable=True)
    workout_minutes = Column(Integer, nullable=True)

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
    focus_category = Column(String(64), nullable=True)  # code, writing, meetings
    notes = Column(String, nullable=True)

    user = relationship("User", back_populates="productivity_entries")


class ProductivityTask(Base):
    __tablename__ = "productivity_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    status = Column(String(32), nullable=False, default="open")  # open, done, cancelled
    due_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="productivity_tasks")


class FocusSession(Base):
    __tablename__ = "focus_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    local_date = Column(Date, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    session_type = Column(String(32), nullable=True)  # pomodoro, deep_work
    notes = Column(String, nullable=True)

    user = relationship("User", back_populates="focus_sessions")


class LearningCourse(Base):
    __tablename__ = "learning_courses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    kind = Column(String(32), nullable=True)  # course, book, topic
    created_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="learning_courses")
    entries = relationship("LearningEntry", back_populates="course")


class LearningEntry(Base, TimestampMixin):
    __tablename__ = "learning_entries"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    study_hours = Column(Float, nullable=False)
    topics = Column(String, nullable=True)
    projects = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    course_id = Column(Integer, ForeignKey("learning_courses.id", ondelete="SET NULL"), nullable=True, index=True)
    source_type = Column(String(32), nullable=True)  # book, course, podcast

    user = relationship("User", back_populates="learning_entries")
    course = relationship("LearningCourse", back_populates="entries")


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="connected")
    access_token = Column(String(512), nullable=True)
    refresh_token = Column(String(512), nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="data_sources")


class SyncJob(Base):
    __tablename__ = "sync_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="queued")
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    message = Column(String(512), nullable=True)
    stats = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)


class UserGoal(Base):
    __tablename__ = "user_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sphere = Column(String(32), nullable=False)
    title = Column(String(255), nullable=False)
    target_value = Column(Float, nullable=True)
    target_metric = Column(String(64), nullable=True)
    deadline = Column(Date, nullable=True)
    archived = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="goals")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    price_monthly = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    is_active = Column(Boolean, nullable=False, default=True)
    features = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    status = Column(String(32), nullable=False, default="active")
    started_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, nullable=False, default=False)
    external_customer_id = Column(String(128), nullable=True)
    external_subscription_id = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
