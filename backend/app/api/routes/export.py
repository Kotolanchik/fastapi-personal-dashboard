import csv
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ... import analytics, models
from ..deps import get_db_session

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
