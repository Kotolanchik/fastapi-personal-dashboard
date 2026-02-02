import csv
import io
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ... import analytics, models
from ..deps import get_current_user, get_db_session

router = APIRouter(tags=["export"])


def _entries_to_csv(entries, fieldnames):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for entry in entries:
        writer.writerow({field: getattr(entry, field) for field in fieldnames})
    return buffer.getvalue()


@router.get("/export")
def export_csv(
    category: str = Query("daily", pattern="^(health|finance|productivity|learning|daily|all)$"),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    category = category.lower()
    filename = f"{category}.csv"

    if category in {"daily", "all"}:
        df = analytics.build_daily_dataframe(db, user_id=user.id)
        csv_body = df.to_csv(index=False)
        return Response(
            content=csv_body,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    if category == "health":
        entries = (
            db.query(models.HealthEntry)
            .filter(models.HealthEntry.user_id == user.id)
            .all()
        )
        fieldnames = [
            "id",
            "user_id",
            "recorded_at",
            "local_date",
            "timezone",
            "entry_type",
            "sleep_hours",
            "energy_level",
            "supplements",
            "weight_kg",
            "wellbeing",
            "notes",
            "steps",
            "heart_rate_avg",
            "workout_minutes",
        ]
        csv_body = _entries_to_csv(entries, fieldnames)
    elif category == "finance":
        entries = (
            db.query(models.FinanceEntry)
            .filter(models.FinanceEntry.user_id == user.id)
            .all()
        )
        fieldnames = [
            "id",
            "user_id",
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
        entries = (
            db.query(models.ProductivityEntry)
            .filter(models.ProductivityEntry.user_id == user.id)
            .all()
        )
        fieldnames = [
            "id",
            "user_id",
            "recorded_at",
            "local_date",
            "timezone",
            "deep_work_hours",
            "tasks_completed",
            "focus_level",
            "focus_category",
            "notes",
        ]
        csv_body = _entries_to_csv(entries, fieldnames)
    else:
        entries = (
            db.query(models.LearningEntry)
            .filter(models.LearningEntry.user_id == user.id)
            .all()
        )
        fieldnames = [
            "id",
            "user_id",
            "recorded_at",
            "local_date",
            "timezone",
            "study_hours",
            "topics",
            "projects",
            "notes",
            "course_id",
            "source_type",
        ]
        csv_body = _entries_to_csv(entries, fieldnames)

    return Response(
        content=csv_body,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/health-report")
def export_health_report(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    """Export health data for a period (e.g. for doctor): CSV with date range in filename."""
    end = end_date or date.today()
    start = start_date or (end - timedelta(days=30))
    entries = (
        db.query(models.HealthEntry)
        .filter(
            models.HealthEntry.user_id == user.id,
            models.HealthEntry.local_date >= start,
            models.HealthEntry.local_date <= end,
        )
        .order_by(models.HealthEntry.local_date.asc(), models.HealthEntry.id.asc())
        .all()
    )
    fieldnames = [
        "local_date",
        "entry_type",
        "sleep_hours",
        "energy_level",
        "wellbeing",
        "weight_kg",
        "steps",
        "heart_rate_avg",
        "workout_minutes",
        "supplements",
        "notes",
    ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for entry in entries:
        row = {f: getattr(entry, f) for f in fieldnames}
        if hasattr(entry, "local_date") and row.get("local_date"):
            row["local_date"] = row["local_date"].isoformat() if hasattr(row["local_date"], "isoformat") else row["local_date"]
        writer.writerow(row)
    filename = f"health_report_{start.isoformat()}_{end.isoformat()}.csv"
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/health-report-pdf")
def export_health_report_pdf(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    user=Depends(get_current_user),
):
    """Stub: PDF export not implemented. Use GET /export/health-report for CSV."""
    from fastapi import HTTPException
    raise HTTPException(
        status_code=501,
        detail="PDF export not implemented. Use GET /export/health-report?start_date=&end_date= for CSV.",
    )
