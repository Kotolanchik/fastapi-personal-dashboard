from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ... import models, schemas
from ...services.entries import apply_timestamp, apply_update, build_entries_query, list_entries
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
    response: Response,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    base = build_entries_query(
        db.query(models.FinanceEntry),
        models.FinanceEntry,
        start_date,
        end_date,
        user_id=user.id,
    )
    total = base.count()
    response.headers["X-Total-Count"] = str(total)
    items = (
        base.order_by(models.FinanceEntry.local_date.desc(), models.FinanceEntry.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return items


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


# --- Expense category mappings (Open Banking -> our fields) ---

@router.get("/category-mappings", response_model=List[schemas.ExpenseCategoryMappingRead])
def list_expense_category_mappings(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    return (
        db.query(models.UserExpenseCategoryMapping)
        .filter(models.UserExpenseCategoryMapping.user_id == user.id)
        .order_by(models.UserExpenseCategoryMapping.provider_category)
        .all()
    )


@router.post("/category-mappings", response_model=schemas.ExpenseCategoryMappingRead, status_code=201)
def create_expense_category_mapping(
    payload: schemas.ExpenseCategoryMappingCreate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    if payload.target_field not in schemas.FINANCE_TARGET_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"target_field must be one of {schemas.FINANCE_TARGET_FIELDS}",
        )
    existing = (
        db.query(models.UserExpenseCategoryMapping)
        .filter(
            models.UserExpenseCategoryMapping.user_id == user.id,
            models.UserExpenseCategoryMapping.provider_category == payload.provider_category,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Mapping for this provider category already exists")
    mapping = models.UserExpenseCategoryMapping(
        user_id=user.id,
        provider_category=payload.provider_category.strip().lower(),
        target_field=payload.target_field,
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.patch("/category-mappings/{mapping_id}", response_model=schemas.ExpenseCategoryMappingRead)
def update_expense_category_mapping(
    mapping_id: int,
    payload: schemas.ExpenseCategoryMappingUpdate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    mapping = (
        db.query(models.UserExpenseCategoryMapping)
        .filter(
            models.UserExpenseCategoryMapping.id == mapping_id,
            models.UserExpenseCategoryMapping.user_id == user.id,
        )
        .first()
    )
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    if payload.target_field is not None and payload.target_field not in schemas.FINANCE_TARGET_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"target_field must be one of {schemas.FINANCE_TARGET_FIELDS}",
        )
    if payload.target_field is not None:
        mapping.target_field = payload.target_field
    db.commit()
    db.refresh(mapping)
    return mapping


@router.delete("/category-mappings/{mapping_id}", status_code=204)
def delete_expense_category_mapping(
    mapping_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    mapping = (
        db.query(models.UserExpenseCategoryMapping)
        .filter(
            models.UserExpenseCategoryMapping.id == mapping_id,
            models.UserExpenseCategoryMapping.user_id == user.id,
        )
        .first()
    )
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    db.delete(mapping)
    db.commit()
