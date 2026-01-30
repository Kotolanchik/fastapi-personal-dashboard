from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ... import models, schemas
from ...services.entries import apply_timestamp, apply_update, list_entries
from ..deps import get_db_session

router = APIRouter(prefix="/learning", tags=["learning"])


@router.post("", response_model=schemas.LearningEntryRead)
def create_learning(entry: schemas.LearningEntryCreate, db: Session = Depends(get_db_session)):
    record = models.LearningEntry(
        study_hours=entry.study_hours,
        topics=entry.topics,
        projects=entry.projects,
        notes=entry.notes,
    )
    apply_timestamp(record, entry.recorded_at, entry.timezone)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=List[schemas.LearningEntryRead])
def list_learning(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db_session),
):
    query = db.query(models.LearningEntry)
    query = list_entries(query, models.LearningEntry, start_date, end_date, limit)
    return query.all()


@router.put("/{entry_id}", response_model=schemas.LearningEntryRead)
def update_learning(
    entry_id: int,
    payload: schemas.LearningEntryUpdate,
    db: Session = Depends(get_db_session),
):
    record = db.get(models.LearningEntry, entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Learning entry not found")
    apply_update(record, payload)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{entry_id}")
def delete_learning(entry_id: int, db: Session = Depends(get_db_session)):
    record = db.get(models.LearningEntry, entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Learning entry not found")
    db.delete(record)
    db.commit()
    return {"status": "deleted"}
