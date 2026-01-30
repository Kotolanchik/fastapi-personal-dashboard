import csv
import io
import os
from datetime import date
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session

from . import analytics, models, schemas
from .database import Base, DATABASE_URL, engine, get_db
from .utils import normalize_datetime


app = FastAPI(title="Personal Life Dashboard MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    if DATABASE_URL.startswith("sqlite"):
        path = DATABASE_URL.replace("sqlite:///", "")
        data_dir = os.path.dirname(path)
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def _apply_timestamp(entry, recorded_at, timezone_name):
    try:
        utc_dt, local_date, tz_name = normalize_datetime(recorded_at, timezone_name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    entry.recorded_at = utc_dt
    entry.local_date = local_date
    entry.timezone = tz_name


def _apply_update(entry, payload):
    data = payload.dict(exclude_unset=True)
    if "recorded_at" in data or "timezone" in data:
        recorded_at = data.get("recorded_at", entry.recorded_at)
        tz_name = data.get("timezone", entry.timezone)
        _apply_timestamp(entry, recorded_at, tz_name)
    for key, value in data.items():
        if key in {"recorded_at", "timezone"}:
            continue
        setattr(entry, key, value)


def _list_entries(
    query,
    model,
    start_date: Optional[date],
    end_date: Optional[date],
    limit: int,
):
    if start_date:
        query = query.filter(model.local_date >= start_date)
    if end_date:
        query = query.filter(model.local_date <= end_date)
    return query.order_by(model.local_date.desc(), model.id.desc()).limit(limit)


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/health", response_model=schemas.HealthEntryRead)
def create_health(entry: schemas.HealthEntryCreate, db: Session = Depends(get_db)):
    record = models.HealthEntry(
        sleep_hours=entry.sleep_hours,
        energy_level=entry.energy_level,
        supplements=entry.supplements,
        weight_kg=entry.weight_kg,
        wellbeing=entry.wellbeing,
        notes=entry.notes,
    )
    _apply_timestamp(record, entry.recorded_at, entry.timezone)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/health", response_model=List[schemas.HealthEntryRead])
def list_health(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(models.HealthEntry)
    query = _list_entries(query, models.HealthEntry, start_date, end_date, limit)
    return query.all()


@app.put("/health/{entry_id}", response_model=schemas.HealthEntryRead)
def update_health(
    entry_id: int,
    payload: schemas.HealthEntryUpdate,
    db: Session = Depends(get_db),
):
    record = db.get(models.HealthEntry, entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Health entry not found")
    _apply_update(record, payload)
    db.commit()
    db.refresh(record)
    return record


@app.delete("/health/{entry_id}")
def delete_health(entry_id: int, db: Session = Depends(get_db)):
    record = db.get(models.HealthEntry, entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Health entry not found")
    db.delete(record)
    db.commit()
    return {"status": "deleted"}


@app.post("/finance", response_model=schemas.FinanceEntryRead)
def create_finance(entry: schemas.FinanceEntryCreate, db: Session = Depends(get_db)):
    record = models.FinanceEntry(
        income=entry.income,
        expense_food=entry.expense_food,
        expense_transport=entry.expense_transport,
        expense_health=entry.expense_health,
        expense_other=entry.expense_other,
        notes=entry.notes,
    )
    _apply_timestamp(record, entry.recorded_at, entry.timezone)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/finance", response_model=List[schemas.FinanceEntryRead])
def list_finance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(models.FinanceEntry)
    query = _list_entries(query, models.FinanceEntry, start_date, end_date, limit)
    return query.all()


@app.put("/finance/{entry_id}", response_model=schemas.FinanceEntryRead)
def update_finance(
    entry_id: int,
    payload: schemas.FinanceEntryUpdate,
    db: Session = Depends(get_db),
):
    record = db.get(models.FinanceEntry, entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Finance entry not found")
    _apply_update(record, payload)
    db.commit()
    db.refresh(record)
    return record


@app.delete("/finance/{entry_id}")
def delete_finance(entry_id: int, db: Session = Depends(get_db)):
    record = db.get(models.FinanceEntry, entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Finance entry not found")
    db.delete(record)
    db.commit()
    return {"status": "deleted"}


@app.post("/productivity", response_model=schemas.ProductivityEntryRead)
def create_productivity(entry: schemas.ProductivityEntryCreate, db: Session = Depends(get_db)):
    record = models.ProductivityEntry(
        deep_work_hours=entry.deep_work_hours,
        tasks_completed=entry.tasks_completed,
        focus_level=entry.focus_level,
        notes=entry.notes,
    )
    _apply_timestamp(record, entry.recorded_at, entry.timezone)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/productivity", response_model=List[schemas.ProductivityEntryRead])
def list_productivity(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(models.ProductivityEntry)
    query = _list_entries(query, models.ProductivityEntry, start_date, end_date, limit)
    return query.all()


@app.put("/productivity/{entry_id}", response_model=schemas.ProductivityEntryRead)
def update_productivity(
    entry_id: int,
    payload: schemas.ProductivityEntryUpdate,
    db: Session = Depends(get_db),
):
    record = db.get(models.ProductivityEntry, entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Productivity entry not found")
    _apply_update(record, payload)
    db.commit()
    db.refresh(record)
    return record


@app.delete("/productivity/{entry_id}")
def delete_productivity(entry_id: int, db: Session = Depends(get_db)):
    record = db.get(models.ProductivityEntry, entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Productivity entry not found")
    db.delete(record)
    db.commit()
    return {"status": "deleted"}


@app.post("/learning", response_model=schemas.LearningEntryRead)
def create_learning(entry: schemas.LearningEntryCreate, db: Session = Depends(get_db)):
    record = models.LearningEntry(
        study_hours=entry.study_hours,
        topics=entry.topics,
        projects=entry.projects,
        notes=entry.notes,
    )
    _apply_timestamp(record, entry.recorded_at, entry.timezone)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/learning", response_model=List[schemas.LearningEntryRead])
def list_learning(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(models.LearningEntry)
    query = _list_entries(query, models.LearningEntry, start_date, end_date, limit)
    return query.all()


@app.put("/learning/{entry_id}", response_model=schemas.LearningEntryRead)
def update_learning(
    entry_id: int,
    payload: schemas.LearningEntryUpdate,
    db: Session = Depends(get_db),
):
    record = db.get(models.LearningEntry, entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Learning entry not found")
    _apply_update(record, payload)
    db.commit()
    db.refresh(record)
    return record


@app.delete("/learning/{entry_id}")
def delete_learning(entry_id: int, db: Session = Depends(get_db)):
    record = db.get(models.LearningEntry, entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Learning entry not found")
    db.delete(record)
    db.commit()
    return {"status": "deleted"}


@app.get("/analytics/correlations", response_model=schemas.CorrelationsResponse)
def correlations(db: Session = Depends(get_db)):
    df = analytics.build_daily_dataframe(db)
    correlations_data = analytics.compute_correlations(df)
    return {"correlations": correlations_data}


@app.get("/analytics/insights", response_model=schemas.InsightsResponse)
def insights(db: Session = Depends(get_db)):
    return analytics.insights_payload(db)


def _entries_to_csv(entries, fieldnames):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for entry in entries:
        writer.writerow({field: getattr(entry, field) for field in fieldnames})
    return buffer.getvalue()


@app.get("/export")
def export_csv(
    category: str = Query("daily", pattern="^(health|finance|productivity|learning|daily|all)$"),
    db: Session = Depends(get_db),
):
    category = category.lower()
    filename = f"{category}.csv"

    if category in {"daily", "all"}:
        df = analytics.build_daily_dataframe(db)
        csv_body = df.to_csv(index=False)
        return Response(
            content=csv_body,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    if category == "health":
        entries = db.query(models.HealthEntry).all()
        fieldnames = [
            "id",
            "recorded_at",
            "local_date",
            "timezone",
            "sleep_hours",
            "energy_level",
            "supplements",
            "weight_kg",
            "wellbeing",
            "notes",
        ]
        csv_body = _entries_to_csv(entries, fieldnames)
    elif category == "finance":
        entries = db.query(models.FinanceEntry).all()
        fieldnames = [
            "id",
            "recorded_at",
            "local_date",
            "timezone",
            "income",
            "expense_food",
            "expense_transport",
            "expense_health",
            "expense_other",
            "notes",
        ]
        csv_body = _entries_to_csv(entries, fieldnames)
    elif category == "productivity":
        entries = db.query(models.ProductivityEntry).all()
        fieldnames = [
            "id",
            "recorded_at",
            "local_date",
            "timezone",
            "deep_work_hours",
            "tasks_completed",
            "focus_level",
            "notes",
        ]
        csv_body = _entries_to_csv(entries, fieldnames)
    else:
        entries = db.query(models.LearningEntry).all()
        fieldnames = [
            "id",
            "recorded_at",
            "local_date",
            "timezone",
            "study_hours",
            "topics",
            "projects",
            "notes",
        ]
        csv_body = _entries_to_csv(entries, fieldnames)

    return Response(
        content=csv_body,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
