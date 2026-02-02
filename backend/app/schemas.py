from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, conint, confloat


class TimestampBase(BaseModel):
    recorded_at: Optional[datetime] = None
    timezone: Optional[str] = Field(default="UTC", max_length=64)


class TimestampRead(BaseModel):
    id: int
    recorded_at: datetime
    local_date: date
    timezone: str

    model_config = ConfigDict(from_attributes=True)


HEALTH_ENTRY_TYPES = ("day", "morning", "evening")
HealthEntryType = Literal["day", "morning", "evening"]


class HealthEntryBase(TimestampBase):
    entry_type: HealthEntryType = "day"
    sleep_hours: confloat(ge=0, le=24)
    energy_level: conint(ge=1, le=10)
    supplements: Optional[str] = None
    weight_kg: Optional[confloat(ge=0, le=500)] = None
    wellbeing: conint(ge=1, le=10)
    notes: Optional[str] = None
    steps: Optional[conint(ge=0, le=100000)] = None
    heart_rate_avg: Optional[conint(ge=30, le=250)] = None
    workout_minutes: Optional[conint(ge=0, le=1440)] = None


class HealthEntryCreate(HealthEntryBase):
    pass


class HealthEntryUpdate(BaseModel):
    recorded_at: Optional[datetime] = None
    timezone: Optional[str] = None
    entry_type: Optional[HealthEntryType] = None
    sleep_hours: Optional[confloat(ge=0, le=24)] = None
    energy_level: Optional[conint(ge=1, le=10)] = None
    supplements: Optional[str] = None
    weight_kg: Optional[confloat(ge=0, le=500)] = None
    wellbeing: Optional[conint(ge=1, le=10)] = None
    notes: Optional[str] = None
    steps: Optional[conint(ge=0, le=100000)] = None
    heart_rate_avg: Optional[conint(ge=30, le=250)] = None
    workout_minutes: Optional[conint(ge=0, le=1440)] = None


class HealthEntryRead(TimestampRead, HealthEntryBase):
    user_id: int


class FinanceEntryBase(TimestampBase):
    income: confloat(ge=0)
    expense_food: confloat(ge=0)
    expense_transport: confloat(ge=0)
    expense_health: confloat(ge=0)
    expense_other: confloat(ge=0)
    notes: Optional[str] = None


class FinanceEntryCreate(FinanceEntryBase):
    pass


class FinanceEntryUpdate(BaseModel):
    recorded_at: Optional[datetime] = None
    timezone: Optional[str] = None
    income: Optional[confloat(ge=0)] = None
    expense_food: Optional[confloat(ge=0)] = None
    expense_transport: Optional[confloat(ge=0)] = None
    expense_health: Optional[confloat(ge=0)] = None
    expense_other: Optional[confloat(ge=0)] = None
    notes: Optional[str] = None


class FinanceEntryRead(TimestampRead, FinanceEntryBase):
    user_id: int


PRODUCTIVITY_TASK_STATUSES = ("open", "done", "cancelled")
FOCUS_CATEGORIES = ("code", "writing", "meetings", "other")
FocusCategoryType = Literal["code", "writing", "meetings", "other"]
SESSION_TYPES = ("pomodoro", "deep_work")
SessionType = Literal["pomodoro", "deep_work"]


class ProductivityTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    status: str = Field(default="open", max_length=32)
    due_at: Optional[datetime] = None


class ProductivityTaskCreate(ProductivityTaskBase):
    pass


class ProductivityTaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=512)
    status: Optional[str] = Field(default=None, max_length=32)
    due_at: Optional[datetime] = None


class ProductivityTaskRead(ProductivityTaskBase):
    id: int
    user_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FocusSessionBase(BaseModel):
    recorded_at: Optional[datetime] = None
    timezone: Optional[str] = Field(default="UTC", max_length=64)
    duration_minutes: conint(ge=1, le=480)
    session_type: Optional[SessionType] = None
    notes: Optional[str] = None


class FocusSessionCreate(FocusSessionBase):
    pass


class FocusSessionRead(BaseModel):
    id: int
    user_id: int
    recorded_at: datetime
    local_date: date
    duration_minutes: int
    session_type: Optional[SessionType] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProductivityEntryBase(TimestampBase):
    deep_work_hours: confloat(ge=0, le=24)
    tasks_completed: conint(ge=0)
    focus_level: conint(ge=1, le=10)
    focus_category: Optional[FocusCategoryType] = None
    notes: Optional[str] = None


class ProductivityEntryCreate(ProductivityEntryBase):
    completed_task_ids: Optional[List[int]] = None  # link tasks_completed to real tasks


class ProductivityEntryUpdate(BaseModel):
    recorded_at: Optional[datetime] = None
    timezone: Optional[str] = None
    deep_work_hours: Optional[confloat(ge=0, le=24)] = None
    tasks_completed: Optional[conint(ge=0)] = None
    focus_level: Optional[conint(ge=1, le=10)] = None
    focus_category: Optional[FocusCategoryType] = None
    notes: Optional[str] = None
    completed_task_ids: Optional[List[int]] = None


class ProductivityEntryRead(TimestampRead, ProductivityEntryBase):
    user_id: int
    completed_task_ids: List[int] = Field(default_factory=list)


# Productivity dashboard
class FocusByCategoryItem(BaseModel):
    category: str
    hours: float


class ProductivityDashboardResponse(BaseModel):
    best_worst_weekday: list  # BestWorstWeekdayItem
    trends_14: list
    trends_30: list
    session_deep_work_hours_total: Optional[float] = None
    top_hours: Optional[List[int]] = None  # hour of day (0-23) with most focus sessions
    focus_by_category: Optional[List[FocusByCategoryItem]] = None
    insight: Optional[str] = None


LEARNING_SOURCE_TYPES = ("book", "course", "podcast", "other")
LearningSourceType = Literal["book", "course", "podcast", "other"]


class LearningCourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    kind: Optional[str] = Field(default=None, max_length=32)  # course, book, topic


class LearningCourseCreate(LearningCourseBase):
    pass


class LearningCourseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    kind: Optional[str] = Field(default=None, max_length=32)
    completed_at: Optional[datetime] = None


class LearningCourseRead(LearningCourseBase):
    id: int
    user_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LearningEntryBase(TimestampBase):
    study_hours: confloat(ge=0, le=24)
    topics: Optional[str] = None
    projects: Optional[str] = None
    notes: Optional[str] = None
    course_id: Optional[int] = None
    source_type: Optional[LearningSourceType] = None


class LearningEntryCreate(LearningEntryBase):
    pass


class LearningEntryUpdate(BaseModel):
    recorded_at: Optional[datetime] = None
    timezone: Optional[str] = None
    study_hours: Optional[confloat(ge=0, le=24)] = None
    topics: Optional[str] = None
    projects: Optional[str] = None
    notes: Optional[str] = None
    course_id: Optional[int] = None
    source_type: Optional[LearningSourceType] = None


class LearningEntryRead(TimestampRead, LearningEntryBase):
    user_id: int


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: int
    default_timezone: Optional[str] = "UTC"
    created_at: datetime
    role: str
    dashboard_settings: Optional[dict] = None
    notification_email: Optional[str] = None
    notification_preferences: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=255)
    default_timezone: Optional[str] = Field(default=None, max_length=64)
    dashboard_settings: Optional[dict] = None
    notification_email: Optional[str] = Field(default=None, max_length=255)
    notification_preferences: Optional[dict] = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=1, max_length=255)
    new_password: str = Field(min_length=8, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Message(BaseModel):
    status: str


class UserRoleUpdate(BaseModel):
    role: str = Field(min_length=3, max_length=32)


class CorrelationItem(BaseModel):
    metric_a: str
    metric_b: str
    correlation: float
    sample_size: int


class CorrelationsResponse(BaseModel):
    correlations: list[CorrelationItem]


class InsightItem(BaseModel):
    message: str
    severity: str = "info"


class InsightsResponse(BaseModel):
    generated_at: datetime
    insights: list[InsightItem]


class OAuthCallbackBody(BaseModel):
    code: str
    state: Optional[str] = None


class DataSourceBase(BaseModel):
    provider: str = Field(min_length=2, max_length=64)
    status: Optional[str] = Field(default="connected", max_length=32)
    metadata: Optional[dict] = Field(default=None, alias="metadata_json")
    sync_settings: Optional[dict] = None  # e.g. {"health": ["steps", "sleep"], "finance": ["*"]}

    model_config = ConfigDict(populate_by_name=True)


class DataSourceCreate(DataSourceBase):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class DataSourceUpdate(BaseModel):
    status: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    metadata: Optional[dict] = Field(default=None, alias="metadata_json")
    sync_settings: Optional[dict] = None

    model_config = ConfigDict(populate_by_name=True)


class DataSourceRead(DataSourceBase):
    id: int
    user_id: int
    last_synced_at: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SyncJobRead(BaseModel):
    id: int
    provider: str
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    message: Optional[str] = None
    stats: Optional[dict] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlanBase(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=128)
    price_monthly: float = Field(ge=0)
    currency: str = Field(default="USD", max_length=8)
    is_active: bool = True
    features: Optional[dict] = None


class PlanCreate(PlanBase):
    pass


class PlanRead(PlanBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionCreate(BaseModel):
    plan_id: int


class SubscriptionRead(BaseModel):
    id: int
    plan_id: int
    status: str
    started_at: datetime
    ends_at: Optional[datetime] = None
    cancel_at_period_end: bool
    external_customer_id: Optional[str] = None
    external_subscription_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationsResponse(BaseModel):
    generated_at: datetime
    recommendations: list[InsightItem]


# Goals
GOAL_SPHERES = ("health", "finance", "productivity", "learning")
GOAL_PROGRESS_PERIODS = ("7d", "month", "deadline")
GOAL_MAX_ACTIVE = 5
GOAL_MAX_PER_SPHERE = 2  # max active goals per sphere (e.g. health, learning)


class GoalBase(BaseModel):
    sphere: str = Field(..., max_length=32)
    title: str = Field(..., min_length=1, max_length=255)
    target_value: Optional[float] = None
    target_metric: Optional[str] = Field(default=None, max_length=64)
    course_id: Optional[int] = None
    deadline: Optional[date] = None


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    sphere: Optional[str] = Field(default=None, max_length=32)
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    target_value: Optional[float] = None
    target_metric: Optional[str] = Field(default=None, max_length=64)
    course_id: Optional[int] = None
    deadline: Optional[date] = None
    archived: Optional[bool] = None


class GoalRead(GoalBase):
    id: int
    user_id: int
    archived: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GoalProgress(BaseModel):
    goal_id: int
    title: str
    sphere: str
    target_value: Optional[float] = None
    target_metric: Optional[str] = None
    course_id: Optional[int] = None
    course_title: Optional[str] = None
    current_value: Optional[float] = None
    progress_pct: Optional[float] = None
    deadline: Optional[date] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None


FINANCE_TARGET_FIELDS = ("income", "expense_food", "expense_transport", "expense_health", "expense_other")


class ExpenseCategoryMappingBase(BaseModel):
    provider_category: str = Field(..., min_length=1, max_length=128)
    target_field: str = Field(..., max_length=64)


class ExpenseCategoryMappingCreate(ExpenseCategoryMappingBase):
    pass


class ExpenseCategoryMappingUpdate(BaseModel):
    target_field: Optional[str] = Field(default=None, max_length=64)


class ExpenseCategoryMappingRead(ExpenseCategoryMappingBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class GoalsProgressResponse(BaseModel):
    goals: list[GoalRead]
    progress: list[GoalProgress]


# Weekly report (digest)
class SphereSummary(BaseModel):
    label: str
    metrics: dict  # e.g. {"sleep_avg": 7.2, "energy_avg": 6}


class WeeklyReportResponse(BaseModel):
    period_start: date
    period_end: date
    summary: dict  # sphere -> SphereSummary or dict of metrics
    insight: Optional[str] = None
    generated_at: datetime


# Trend this month (dashboard)
class TrendThisMonthItem(BaseModel):
    metric: str
    label: str
    value: float
    direction: str  # "up" | "down" | "neutral"


class TrendThisMonthResponse(BaseModel):
    metrics: list[TrendThisMonthItem]


# Insight of the week (dashboard)
class InsightOfTheWeekResponse(BaseModel):
    insight: Optional[str] = None


# Weekday and linear trends (best/worst weekday, 14/30 day trends)
class BestWorstWeekdayItem(BaseModel):
    metric: str
    best_weekday: str
    worst_weekday: str
    best_value: float
    worst_value: float


class LinearTrendItem(BaseModel):
    metric: str
    slope: float
    direction: str  # "up" | "down" | "neutral"
    days: int


class WeekdayTrendsResponse(BaseModel):
    best_worst_weekday: list[BestWorstWeekdayItem]
    trends_14: list[LinearTrendItem]
    trends_30: list[LinearTrendItem]


# LLM / AI Assistant
class LlmChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    context: Optional[str] = Field(default=None, max_length=8000)


class LlmChatResponse(BaseModel):
    reply: str
    model: Optional[str] = None


class LlmInsightsResponse(BaseModel):
    insight: str
    model: Optional[str] = None
