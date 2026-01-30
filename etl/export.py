import argparse
import os

from sqlalchemy.orm import Session

from backend.app import analytics, models
from backend.app.database import SessionLocal


def export_table(entries, fieldnames, output_path):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        handle.write(",".join(fieldnames))
        handle.write("\n")
        for entry in entries:
            row = [str(getattr(entry, field, "")) for field in fieldnames]
            handle.write(",".join(row))
            handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Export dashboard data to CSV.")
    parser.add_argument("--category", default="daily", help="health|finance|productivity|learning|daily")
    parser.add_argument("--output", default="exports", help="Output directory")
    parser.add_argument("--user-id", type=int, default=None, help="Filter by user id")
    args = parser.parse_args()

    category = args.category.lower()
    output_dir = args.output
    user_id = args.user_id

    db: Session = SessionLocal()
    try:
        if category == "daily":
            df = analytics.build_daily_dataframe(db, user_id=user_id)
            output_path = os.path.join(output_dir, "daily.csv")
            os.makedirs(output_dir, exist_ok=True)
            df.to_csv(output_path, index=False)
            return

        if category == "health":
            query = db.query(models.HealthEntry)
            if user_id is not None:
                query = query.filter(models.HealthEntry.user_id == user_id)
            entries = query.all()
            fieldnames = [
                "id",
                "user_id",
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
        elif category == "finance":
            query = db.query(models.FinanceEntry)
            if user_id is not None:
                query = query.filter(models.FinanceEntry.user_id == user_id)
            entries = query.all()
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
        elif category == "productivity":
            query = db.query(models.ProductivityEntry)
            if user_id is not None:
                query = query.filter(models.ProductivityEntry.user_id == user_id)
            entries = query.all()
            fieldnames = [
                "id",
                "user_id",
                "recorded_at",
                "local_date",
                "timezone",
                "deep_work_hours",
                "tasks_completed",
                "focus_level",
                "notes",
            ]
        elif category == "learning":
            query = db.query(models.LearningEntry)
            if user_id is not None:
                query = query.filter(models.LearningEntry.user_id == user_id)
            entries = query.all()
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
            ]
        else:
            raise ValueError("Unsupported category.")

        output_path = os.path.join(output_dir, f"{category}.csv")
        export_table(entries, fieldnames, output_path)
    finally:
        db.close()


if __name__ == "__main__":
    main()
