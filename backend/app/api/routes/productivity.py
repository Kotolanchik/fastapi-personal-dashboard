from datetime import date, datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ... import models, schemas
from ...services.entries import apply_timestamp, apply_update, list_entries
from ...utils import normalize_datetime
from ..deps import get_current_user, get_db_session

router = APIRouter(prefix="/productivity", tags=["productivity"])


@router.post("", response_model=schemas.ProductivityEntryRead)
def create_productivity(
    entry: schemas.ProductivityEntryCreate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    record = models.ProductivityEntry(
        user_id=user.id,
        deep_work_hours=entry.deep_work_hours,
        tasks_completed=entry.tasks_completed,
        focus_level=entry.focus_level,
        focus_category=entry.focus_category,
        notes=entry.notes,
    )
    apply_timestamp(record, entry.recorded_at, entry.timezone)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=List[schemas.ProductivityEntryRead])
def list_productivity(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    query = db.query(models.ProductivityEntry)
    query = list_entries(
        query,
        models.ProductivityEntry,
        start_date,
        end_date,
        limit,
        user_id=user.id,
    )
    return query.all()


@router.put("/{entry_id}", response_model=schemas.ProductivityEntryRead)
def update_productivity(
    entry_id: int,
    payload: schemas.ProductivityEntryUpdate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    record = (
        db.query(models.ProductivityEntry)
        .filter(
            models.ProductivityEntry.id == entry_id,
            models.ProductivityEntry.user_id == user.id,
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Productivity entry not found")
    apply_update(record, payload)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{entry_id}")
def delete_productivity(
    entry_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    record = (
        db.query(models.ProductivityEntry)
        .filter(
            models.ProductivityEntry.id == entry_id,
            models.ProductivityEntry.user_id == user.id,
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Productivity entry not found")
    db.delete(record)
    db.commit()
    return {"status": "deleted"}


# --- Productivity tasks ---

@router.post("/tasks", response_model=schemas.ProductivityTaskRead)
def create_task(
    payload: schemas.ProductivityTaskCreate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    task = models.ProductivityTask(
        user_id=user.id,
        title=payload.title,
        status=payload.status or "open",
        due_at=payload.due_at,
        created_at=datetime.now(timezone.utc),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks", response_model=List[schemas.ProductivityTaskRead])
def list_tasks(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    q = db.query(models.ProductivityTask).filter(models.ProductivityTask.user_id == user.id)
    if status:
        q = q.filter(models.ProductivityTask.status == status)
    return q.order_by(models.ProductivityTask.created_at.desc()).all()


@router.get("/tasks/{task_id}", response_model=schemas.ProductivityTaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    task = db.query(models.ProductivityTask).filter(
        models.ProductivityTask.id == task_id,
        models.ProductivityTask.user_id == user.id,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=schemas.ProductivityTaskRead)
def update_task(
    task_id: int,
    payload: schemas.ProductivityTaskUpdate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    task = db.query(models.ProductivityTask).filter(
        models.ProductivityTask.id == task_id,
        models.ProductivityTask.user_id == user.id,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(task, key, value)
    if data.get("status") == "done" and task.completed_at is None:
        task.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    task = db.query(models.ProductivityTask).filter(
        models.ProductivityTask.id == task_id,
        models.ProductivityTask.user_id == user.id,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"status": "deleted"}


# --- Focus sessions (Pomodoro / timers) ---

@router.post("/sessions", response_model=schemas.FocusSessionRead)
def create_focus_session(
    payload: schemas.FocusSessionCreate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    try:
        utc_dt, local_date, _ = normalize_datetime(payload.recorded_at, payload.timezone)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    session = models.FocusSession(
        user_id=user.id,
        recorded_at=utc_dt,
        local_date=local_date,
        duration_minutes=payload.duration_minutes,
        session_type=payload.session_type,
        notes=payload.notes,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=List[schemas.FocusSessionRead])
def list_focus_sessions(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    q = db.query(models.FocusSession).filter(models.FocusSession.user_id == user.id)
    if start_date:
        q = q.filter(models.FocusSession.local_date >= start_date)
    if end_date:
        q = q.filter(models.FocusSession.local_date <= end_date)
    return q.order_by(models.FocusSession.local_date.desc(), models.FocusSession.id.desc()).limit(limit).all()
