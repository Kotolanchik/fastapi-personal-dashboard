from datetime import date, datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ... import models, schemas
from ...services.entries import apply_timestamp, apply_update, build_entries_query, list_entries
from ..deps import get_current_user, get_db_session

router = APIRouter(prefix="/learning", tags=["learning"])


@router.post("", response_model=schemas.LearningEntryRead)
def create_learning(
    entry: schemas.LearningEntryCreate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    record = models.LearningEntry(
        user_id=user.id,
        study_hours=entry.study_hours,
        topics=entry.topics,
        projects=entry.projects,
        notes=entry.notes,
        course_id=entry.course_id,
        source_type=entry.source_type,
    )
    apply_timestamp(record, entry.recorded_at, entry.timezone)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=List[schemas.LearningEntryRead])
def list_learning(
    response: Response,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    base = build_entries_query(
        db.query(models.LearningEntry),
        models.LearningEntry,
        start_date,
        end_date,
        user_id=user.id,
    )
    total = base.count()
    response.headers["X-Total-Count"] = str(total)
    items = (
        base.order_by(models.LearningEntry.local_date.desc(), models.LearningEntry.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return items


@router.put("/{entry_id}", response_model=schemas.LearningEntryRead)
def update_learning(
    entry_id: int,
    payload: schemas.LearningEntryUpdate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    record = (
        db.query(models.LearningEntry)
        .filter(models.LearningEntry.id == entry_id, models.LearningEntry.user_id == user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Learning entry not found")
    apply_update(record, payload)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{entry_id}")
def delete_learning(
    entry_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    record = (
        db.query(models.LearningEntry)
        .filter(models.LearningEntry.id == entry_id, models.LearningEntry.user_id == user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Learning entry not found")
    db.delete(record)
    db.commit()
    return {"status": "deleted"}


# --- Learning courses (topics/courses reference) ---

@router.post("/courses", response_model=schemas.LearningCourseRead)
def create_course(
    payload: schemas.LearningCourseCreate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    course = models.LearningCourse(
        user_id=user.id,
        title=payload.title,
        kind=payload.kind,
        created_at=datetime.now(timezone.utc),
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/courses", response_model=List[schemas.LearningCourseRead])
def list_courses(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    return db.query(models.LearningCourse).filter(models.LearningCourse.user_id == user.id).order_by(models.LearningCourse.id).all()


@router.get("/courses/{course_id}", response_model=schemas.LearningCourseRead)
def get_course(
    course_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    course = db.query(models.LearningCourse).filter(
        models.LearningCourse.id == course_id,
        models.LearningCourse.user_id == user.id,
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/courses/{course_id}", response_model=schemas.LearningCourseRead)
def update_course(
    course_id: int,
    payload: schemas.LearningCourseUpdate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    course = db.query(models.LearningCourse).filter(
        models.LearningCourse.id == course_id,
        models.LearningCourse.user_id == user.id,
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/courses/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    course = db.query(models.LearningCourse).filter(
        models.LearningCourse.id == course_id,
        models.LearningCourse.user_id == user.id,
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return {"status": "deleted"}


@router.get("/streak")
def learning_streak(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    """Current consecutive days with at least one learning entry (streak)."""
    from datetime import timedelta

    today = date.today()
    last = (
        db.query(models.LearningEntry.local_date)
        .filter(models.LearningEntry.user_id == user.id)
        .order_by(models.LearningEntry.local_date.desc())
        .limit(1)
        .scalar()
    )
    if last is None:
        return {"current_streak_days": 0, "last_activity_date": None}
    if last < today - timedelta(days=1):
        return {"current_streak_days": 0, "last_activity_date": last.isoformat()}
    streak = 0
    d = today
    while True:
        exists = (
            db.query(models.LearningEntry)
            .filter(
                models.LearningEntry.user_id == user.id,
                models.LearningEntry.local_date == d,
            )
            .limit(1)
            .first()
        )
        if not exists:
            break
        streak += 1
        d -= timedelta(days=1)
    return {
        "current_streak_days": streak,
        "last_activity_date": last.isoformat(),
    }
