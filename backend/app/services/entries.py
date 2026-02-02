from datetime import date
from typing import Optional

from fastapi import HTTPException

from ..utils import normalize_datetime


def apply_timestamp(entry, recorded_at, timezone_name):
    try:
        utc_dt, local_date, tz_name = normalize_datetime(recorded_at, timezone_name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    entry.recorded_at = utc_dt
    entry.local_date = local_date
    entry.timezone = tz_name


def apply_update(entry, payload):
    dump = getattr(payload, "model_dump", None)
    data = dump(exclude_unset=True) if dump else payload.dict(exclude_unset=True)
    if "recorded_at" in data or "timezone" in data:
        recorded_at = data.get("recorded_at", entry.recorded_at)
        tz_name = data.get("timezone", entry.timezone)
        apply_timestamp(entry, recorded_at, tz_name)
    for key, value in data.items():
        if key in {"recorded_at", "timezone"}:
            continue
        setattr(entry, key, value)


def build_entries_query(
    query,
    model,
    start_date: Optional[date],
    end_date: Optional[date],
    user_id: Optional[int] = None,
):
    """Return filtered query (no order/limit/offset) for count or list with pagination."""
    if user_id is not None:
        query = query.filter(model.user_id == user_id)
    if start_date:
        query = query.filter(model.local_date >= start_date)
    if end_date:
        query = query.filter(model.local_date <= end_date)
    return query


def list_entries(
    query,
    model,
    start_date: Optional[date],
    end_date: Optional[date],
    limit: int,
    user_id: Optional[int] = None,
    offset: int = 0,
):
    q = build_entries_query(query, model, start_date, end_date, user_id)
    return q.order_by(model.local_date.desc(), model.id.desc()).offset(offset).limit(limit)
