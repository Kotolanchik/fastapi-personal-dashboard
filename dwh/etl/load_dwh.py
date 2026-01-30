import argparse
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app import models as app_models
from backend.app.database import SessionLocal as AppSession
from dwh import models as dwh_models
from dwh.database import SessionLocal as DwhSession


def ensure_dim_user(dwh_db: Session, app_user: app_models.User, cache: dict[int, dwh_models.DimUser]):
    if app_user.id in cache:
        return cache[app_user.id]
    dim = dwh_models.DimUser(
        user_id=app_user.id,
        email=app_user.email,
        full_name=app_user.full_name,
        created_at=app_user.created_at,
    )
    dwh_db.add(dim)
    dwh_db.commit()
    dwh_db.refresh(dim)
    cache[app_user.id] = dim
    return dim


def ensure_dim_date(dwh_db: Session, day, cache: dict):
    if day in cache:
        return cache[day]
    dim = dwh_models.DimDate(
        date=day,
        year=day.year,
        month=day.month,
        day=day.day,
    )
    dwh_db.add(dim)
    dwh_db.commit()
    dwh_db.refresh(dim)
    cache[day] = dim
    return dim


def upsert_fact(dwh_db: Session, model, payloads):
    for payload in payloads:
        exists = (
            dwh_db.query(model)
            .filter(
                model.user_id == payload["user_id"],
                model.source_entry_id == payload["source_entry_id"],
            )
            .first()
        )
        if exists:
            continue
        dwh_db.add(model(**payload))
    dwh_db.commit()


def main():
    parser = argparse.ArgumentParser(description="Load app data into DWH schema.")
    parser.add_argument("--user-id", type=int, default=None, help="Load only one user")
    args = parser.parse_args()

    app_db: Session = AppSession()
    dwh_db: Session = DwhSession()
    try:
        dim_user_cache = {user.user_id: user for user in dwh_db.query(dwh_models.DimUser).all()}
        dim_date_cache = {day.date: day for day in dwh_db.query(dwh_models.DimDate).all()}

        user_query = app_db.query(app_models.User)
        if args.user_id is not None:
            user_query = user_query.filter(app_models.User.id == args.user_id)
        app_users = user_query.all()

        for app_user in app_users:
            ensure_dim_user(dwh_db, app_user, dim_user_cache)

        loaded_at = datetime.now(timezone.utc)

        def build_payload(entry, date_id):
            return {
                "source_entry_id": entry.id,
                "user_id": entry.user_id,
                "date_id": date_id,
                "recorded_at": entry.recorded_at,
                "loaded_at": loaded_at,
            }

        health_entries = app_db.query(app_models.HealthEntry)
        finance_entries = app_db.query(app_models.FinanceEntry)
        productivity_entries = app_db.query(app_models.ProductivityEntry)
        learning_entries = app_db.query(app_models.LearningEntry)

        if args.user_id is not None:
            health_entries = health_entries.filter(app_models.HealthEntry.user_id == args.user_id)
            finance_entries = finance_entries.filter(app_models.FinanceEntry.user_id == args.user_id)
            productivity_entries = productivity_entries.filter(
                app_models.ProductivityEntry.user_id == args.user_id
            )
            learning_entries = learning_entries.filter(
                app_models.LearningEntry.user_id == args.user_id
            )

        health_payloads = []
        for entry in health_entries.all():
            dim_date = ensure_dim_date(dwh_db, entry.local_date, dim_date_cache)
            payload = build_payload(entry, dim_date.date_id)
            payload.update(
                {
                    "sleep_hours": entry.sleep_hours,
                    "energy_level": entry.energy_level,
                    "weight_kg": entry.weight_kg,
                    "wellbeing": entry.wellbeing,
                }
            )
            health_payloads.append(payload)

        finance_payloads = []
        for entry in finance_entries.all():
            dim_date = ensure_dim_date(dwh_db, entry.local_date, dim_date_cache)
            payload = build_payload(entry, dim_date.date_id)
            payload.update(
                {
                    "income": entry.income,
                    "expense_food": entry.expense_food,
                    "expense_transport": entry.expense_transport,
                    "expense_health": entry.expense_health,
                    "expense_other": entry.expense_other,
                }
            )
            finance_payloads.append(payload)

        productivity_payloads = []
        for entry in productivity_entries.all():
            dim_date = ensure_dim_date(dwh_db, entry.local_date, dim_date_cache)
            payload = build_payload(entry, dim_date.date_id)
            payload.update(
                {
                    "deep_work_hours": entry.deep_work_hours,
                    "tasks_completed": entry.tasks_completed,
                    "focus_level": entry.focus_level,
                }
            )
            productivity_payloads.append(payload)

        learning_payloads = []
        for entry in learning_entries.all():
            dim_date = ensure_dim_date(dwh_db, entry.local_date, dim_date_cache)
            payload = build_payload(entry, dim_date.date_id)
            payload.update({"study_hours": entry.study_hours})
            learning_payloads.append(payload)

        upsert_fact(dwh_db, dwh_models.FactHealth, health_payloads)
        upsert_fact(dwh_db, dwh_models.FactFinance, finance_payloads)
        upsert_fact(dwh_db, dwh_models.FactProductivity, productivity_payloads)
        upsert_fact(dwh_db, dwh_models.FactLearning, learning_payloads)
    finally:
        app_db.close()
        dwh_db.close()


if __name__ == "__main__":
    main()
