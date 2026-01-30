from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, conint, confloat


class TimestampBase(BaseModel):
    recorded_at: Optional[datetime] = None
    timezone: Optional[str] = Field(default="UTC", max_length=64)


class TimestampRead(BaseModel):
    id: int
    recorded_at: datetime
    local_date: date
    timezone: str

    class Config:
        orm_mode = True


class HealthEntryBase(TimestampBase):
    sleep_hours: confloat(ge=0, le=24)
    energy_level: conint(ge=1, le=10)
    supplements: Optional[str] = None
    weight_kg: Optional[confloat(ge=0, le=500)] = None
    wellbeing: conint(ge=1, le=10)
    notes: Optional[str] = None


class HealthEntryCreate(HealthEntryBase):
    pass


class HealthEntryUpdate(BaseModel):
    recorded_at: Optional[datetime] = None
    timezone: Optional[str] = None
    sleep_hours: Optional[confloat(ge=0, le=24)] = None
    energy_level: Optional[conint(ge=1, le=10)] = None
    supplements: Optional[str] = None
    weight_kg: Optional[confloat(ge=0, le=500)] = None
    wellbeing: Optional[conint(ge=1, le=10)] = None
    notes: Optional[str] = None


class HealthEntryRead(TimestampRead, HealthEntryBase):
    pass


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
    pass


class ProductivityEntryBase(TimestampBase):
    deep_work_hours: confloat(ge=0, le=24)
    tasks_completed: conint(ge=0)
    focus_level: conint(ge=1, le=10)
    notes: Optional[str] = None


class ProductivityEntryCreate(ProductivityEntryBase):
    pass


class ProductivityEntryUpdate(BaseModel):
    recorded_at: Optional[datetime] = None
    timezone: Optional[str] = None
    deep_work_hours: Optional[confloat(ge=0, le=24)] = None
    tasks_completed: Optional[conint(ge=0)] = None
    focus_level: Optional[conint(ge=1, le=10)] = None
    notes: Optional[str] = None


class ProductivityEntryRead(TimestampRead, ProductivityEntryBase):
    pass


class LearningEntryBase(TimestampBase):
    study_hours: confloat(ge=0, le=24)
    topics: Optional[str] = None
    projects: Optional[str] = None
    notes: Optional[str] = None


class LearningEntryCreate(LearningEntryBase):
    pass


class LearningEntryUpdate(BaseModel):
    recorded_at: Optional[datetime] = None
    timezone: Optional[str] = None
    study_hours: Optional[confloat(ge=0, le=24)] = None
    topics: Optional[str] = None
    projects: Optional[str] = None
    notes: Optional[str] = None


class LearningEntryRead(TimestampRead, LearningEntryBase):
    pass


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
