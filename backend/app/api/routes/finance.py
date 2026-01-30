from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ... import models, schemas
from ...services.entries import apply_timestamp, apply_update, list_entries
from ..deps import get_current_user, get_db_session

router = APIRouter(prefix="/finance", tags=["finance"])


@router.post("", response_model=schemas.FinanceEntryRead)
def create_finance(
    entry: schemas.FinanceEntryCreate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    record = models.FinanceEntry(
        user_id=user.id,
        income=entry.income,
        expense_food=entry.expense_food,
        expense_transport=entry.expense_transport,
        expense_health=entry.expense_health,
        expense_other=entry.expense_other,
        notes=entry.notes,
    )
    apply_timestamp(record, entry.recorded_at, entry.timezone)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=List[schemas.FinanceEntryRead])
def list_finance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    query = db.query(models.FinanceEntry)
    query = list_entries(
        query,
        models.FinanceEntry,
        start_date,
        end_date,
        limit,
        user_id=user.id,
    )
    return query.all()


@router.put("/{entry_id}", response_model=schemas.FinanceEntryRead)
def update_finance(
    entry_id: int,
    payload: schemas.FinanceEntryUpdate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    record = (
        db.query(models.FinanceEntry)
        .filter(models.FinanceEntry.id == entry_id, models.FinanceEntry.user_id == user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Finance entry not found")
    apply_update(record, payload)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{entry_id}")
def delete_finance(
    entry_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    record = (
        db.query(models.FinanceEntry)
        .filter(models.FinanceEntry.id == entry_id, models.FinanceEntry.user_id == user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Finance entry not found")
    db.delete(record)
    db.commit()
    return {"status": "deleted"}
