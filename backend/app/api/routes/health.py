from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ... import models, schemas
from ...services.entries import apply_timestamp, apply_update, build_entries_query, list_entries
from ..deps import get_current_user, get_db_session

router = APIRouter(prefix="/health", tags=["health"])


@router.post("", response_model=schemas.HealthEntryRead)
def create_health(
    entry: schemas.HealthEntryCreate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    record = models.HealthEntry(
        user_id=user.id,
        entry_type=entry.entry_type or "day",
        sleep_hours=entry.sleep_hours,
        energy_level=entry.energy_level,
        supplements=entry.supplements,
        weight_kg=entry.weight_kg,
        wellbeing=entry.wellbeing,
        notes=entry.notes,
        steps=entry.steps,
        heart_rate_avg=entry.heart_rate_avg,
        workout_minutes=entry.workout_minutes,
    )
    apply_timestamp(record, entry.recorded_at, entry.timezone)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=List[schemas.HealthEntryRead])
def list_health(
    response: Response,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    base = build_entries_query(
        db.query(models.HealthEntry),
        models.HealthEntry,
        start_date,
        end_date,
        user_id=user.id,
    )
    total = base.count()
    response.headers["X-Total-Count"] = str(total)
    items = (
        base.order_by(models.HealthEntry.local_date.desc(), models.HealthEntry.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return items


@router.put("/{entry_id}", response_model=schemas.HealthEntryRead)
def update_health(
    entry_id: int,
    payload: schemas.HealthEntryUpdate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    record = (
        db.query(models.HealthEntry)
        .filter(models.HealthEntry.id == entry_id, models.HealthEntry.user_id == user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Health entry not found")
    apply_update(record, payload)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{entry_id}")
def delete_health(
    entry_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    record = (
        db.query(models.HealthEntry)
        .filter(models.HealthEntry.id == entry_id, models.HealthEntry.user_id == user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Health entry not found")
    db.delete(record)
    db.commit()
    return {"status": "deleted"}
