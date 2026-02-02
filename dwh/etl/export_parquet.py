import argparse
import os

import pandas as pd
from sqlalchemy.orm import Session

from backend.app import models
from backend.app.database import SessionLocal


def export_dataframe(df: pd.DataFrame, output_dir: str, name: str):
    if df.empty:
        return
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{name}.parquet")
    df.to_parquet(output_path, index=False)


def load_table(db: Session, model, user_id: int | None = None):
    query = db.query(model)
    if user_id is not None:
        query = query.filter(model.user_id == user_id)
    return pd.read_sql(query.statement, db.bind)


def main():
    parser = argparse.ArgumentParser(description="Export app data to Parquet files.")
    parser.add_argument("--output", default="dwh/parquet", help="Output directory")
    parser.add_argument("--user-id", type=int, default=None, help="Filter by user id")
    args = parser.parse_args()

    output_dir = args.output
    user_id = args.user_id

    db: Session = SessionLocal()
    try:
        export_dataframe(
            load_table(db, models.HealthEntry, user_id=user_id),
            os.path.join(output_dir, "health"),
            "health",
        )
        export_dataframe(
            load_table(db, models.FinanceEntry, user_id=user_id),
            os.path.join(output_dir, "finance"),
            "finance",
        )
        export_dataframe(
            load_table(db, models.ProductivityEntry, user_id=user_id),
            os.path.join(output_dir, "productivity"),
            "productivity",
        )
        export_dataframe(
            load_table(db, models.LearningEntry, user_id=user_id),
            os.path.join(output_dir, "learning"),
            "learning",
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
