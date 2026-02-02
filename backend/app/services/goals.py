"""Goals CRUD and progress computation."""

from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from .. import models, schemas

# Map (sphere, target_metric) -> (model, field, agg: 'avg'|'sum')
METRIC_SOURCE = {
    ("health", "sleep_hours"): (models.HealthEntry, "sleep_hours", "avg"),
    ("health", "energy_level"): (models.HealthEntry, "energy_level", "avg"),
    ("health", "wellbeing"): (models.HealthEntry, "wellbeing", "avg"),
    ("health", "steps"): (models.HealthEntry, "steps", "sum"),
    ("health", "workout_minutes"): (models.HealthEntry, "workout_minutes", "sum"),
    ("finance", "income"): (models.FinanceEntry, "income", "sum"),
    ("finance", "expense_total"): (models.FinanceEntry, None, "sum_expenses"),
    ("productivity", "deep_work_hours"): (models.ProductivityEntry, "deep_work_hours", "sum"),
    ("productivity", "tasks_completed"): (models.ProductivityEntry, "tasks_completed", "sum"),
    ("productivity", "focus_level"): (models.ProductivityEntry, "focus_level", "avg"),
    ("learning", "study_hours"): (models.LearningEntry, "study_hours", "sum"),
}


def list_goals(
    db: Session,
    user_id: int,
    include_archived: bool = False,
) -> List[models.UserGoal]:
    q = db.query(models.UserGoal).filter(models.UserGoal.user_id == user_id)
    if not include_archived:
        q = q.filter(models.UserGoal.archived == False)  # noqa: E712
    return q.order_by(models.UserGoal.id).all()


def get_goal(db: Session, goal_id: int, user_id: int) -> Optional[models.UserGoal]:
    return db.query(models.UserGoal).filter(
        models.UserGoal.id == goal_id,
        models.UserGoal.user_id == user_id,
    ).first()


def count_active_goals_by_sphere(db: Session, user_id: int, sphere: str) -> int:
    return (
        db.query(models.UserGoal)
        .filter(
            models.UserGoal.user_id == user_id,
            models.UserGoal.sphere == sphere,
            models.UserGoal.archived == False,  # noqa: E712
        )
        .count()
    )


def create_goal(db: Session, user_id: int, payload: schemas.GoalCreate) -> models.UserGoal:
    goal = models.UserGoal(
        user_id=user_id,
        sphere=payload.sphere,
        title=payload.title,
        target_value=payload.target_value,
        target_metric=payload.target_metric,
        course_id=payload.course_id if hasattr(payload, "course_id") else None,
        deadline=payload.deadline,
        archived=False,
        created_at=datetime.now(timezone.utc),
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def update_goal(
    db: Session,
    goal: models.UserGoal,
    payload: schemas.GoalUpdate,
) -> models.UserGoal:
    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(goal, key, value)
    db.commit()
    db.refresh(goal)
    return goal


def delete_goal(db: Session, goal: models.UserGoal) -> None:
    db.delete(goal)
    db.commit()


def _period_to_dates(
    period: str,
    goal: Optional[models.UserGoal] = None,
) -> tuple[date, date]:
    today = date.today()
    if period == "7d":
        return today - timedelta(days=7), today
    if period == "month":
        start = today.replace(day=1)
        return start, today
    if period == "deadline" and goal and goal.deadline:
        end = min(goal.deadline, today)
        start = end - timedelta(days=30)
        return start, end
    # default
    return today - timedelta(days=7), today


def _current_value_for_goal(
    db: Session,
    user_id: int,
    sphere: str,
    target_metric: Optional[str],
    start_date: date,
    end_date: date,
) -> Optional[float]:
    if not target_metric:
        return None
    key = (sphere, target_metric)
    if key not in METRIC_SOURCE:
        return None
    model, field, agg = METRIC_SOURCE[key]
    query = db.query(model).filter(
        model.user_id == user_id,
        model.local_date >= start_date,
        model.local_date <= end_date,
    )
    entries = query.all()
    if not entries:
        return None
    if agg == "sum_expenses":
        return sum(
            e.expense_food + e.expense_transport + e.expense_health + e.expense_other
            for e in entries
        )
    if agg == "avg":
        vals = [getattr(e, field) for e in entries if getattr(e, field) is not None]
        return sum(vals) / len(vals) if vals else None
    return sum(getattr(e, field) or 0 for e in entries)


def compute_goal_progress(
    db: Session,
    user_id: int,
    goal: models.UserGoal,
    period: str = "7d",
) -> schemas.GoalProgress:
    course_id = getattr(goal, "course_id", None)
    course_title = None
    current = None
    progress_pct = None

    if goal.target_metric == "course_complete" and course_id:
        course = (
            db.query(models.LearningCourse)
            .filter(
                models.LearningCourse.id == course_id,
                models.LearningCourse.user_id == user_id,
            )
            .first()
        )
        if course:
            course_title = course.title
            if getattr(course, "completed_at", None):
                current = 1.0
                progress_pct = 100.0
            else:
                current = 0.0
                progress_pct = 0.0
        start_date, end_date = _period_to_dates(period, goal)
        return schemas.GoalProgress(
            goal_id=goal.id,
            title=goal.title,
            sphere=goal.sphere,
            target_value=goal.target_value,
            target_metric=goal.target_metric,
            course_id=course_id,
            course_title=course_title,
            current_value=current,
            progress_pct=progress_pct,
            deadline=goal.deadline,
            period_start=start_date,
            period_end=end_date,
        )

    start_date, end_date = _period_to_dates(period, goal)
    current = _current_value_for_goal(
        db, user_id, goal.sphere, goal.target_metric, start_date, end_date
    )
    if goal.target_value is not None and current is not None and goal.target_value > 0:
        progress_pct = min(100.0, (current / goal.target_value) * 100.0)
    return schemas.GoalProgress(
        goal_id=goal.id,
        title=goal.title,
        sphere=goal.sphere,
        target_value=goal.target_value,
        target_metric=goal.target_metric,
        course_id=course_id,
        course_title=course_title,
        current_value=current,
        progress_pct=progress_pct,
        deadline=goal.deadline,
        period_start=start_date,
        period_end=end_date,
    )


def get_goals_with_progress(
    db: Session,
    user_id: int,
    period: str = "7d",
    include_archived: bool = False,
) -> schemas.GoalsProgressResponse:
    goals = list_goals(db, user_id, include_archived=include_archived)
    progress = [compute_goal_progress(db, user_id, g, period=period) for g in goals]
    return schemas.GoalsProgressResponse(goals=goals, progress=progress)
