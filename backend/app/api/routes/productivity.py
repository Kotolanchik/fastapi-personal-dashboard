from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ... import models, schemas
from ...services.entries import apply_timestamp, apply_update, list_entries
from ..deps import get_db_session

router = APIRouter(prefix="/productivity", tags=["productivity"])


@router.post("", response_model=schemas.ProductivityEntryRead)
def create_productivity(
    entry: schemas.ProductivityEntryCreate, db: Session = Depends(get_db_session)
):
    record = models.ProductivityEntry(
        deep_work_hours=entry.deep_work_hours,
        tasks_completed=entry.tasks_completed,
        focus_level=entry.focus_level,
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
):
    query = db.query(models.ProductivityEntry)
    query = list_entries(query, models.ProductivityEntry, start_date, end_date, limit)
    return query.all()


@router.put("/{entry_id}", response_model=schemas.ProductivityEntryRead)
def update_productivity(
    entry_id: int,
    payload: schemas.ProductivityEntryUpdate,
    db: Session = Depends(get_db_session),
):
    record = db.get(models.ProductivityEntry, entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Productivity entry not found")
    apply_update(record, payload)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{entry_id}")
def delete_productivity(entry_id: int, db: Session = Depends(get_db_session)):
    record = db.get(models.ProductivityEntry, entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Productivity entry not found")
    db.delete(record)
    db.commit()
    return {"status": "deleted"}
