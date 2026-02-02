from datetime import date, datetime, timezone
from typing import Optional, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def normalize_datetime(
    recorded_at: Optional[datetime],
    timezone_name: Optional[str],
) -> Tuple[datetime, date, str]:
    tz = None
    if timezone_name:
        try:
            tz = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Invalid timezone '{timezone_name}'") from exc

    if recorded_at is None:
        recorded_at = datetime.now(tz or timezone.utc)

    if recorded_at.tzinfo is None:
        tz = tz or timezone.utc
        recorded_at = recorded_at.replace(tzinfo=tz)

    tz = tz or recorded_at.tzinfo or timezone.utc
    local_dt = recorded_at.astimezone(tz)
    local_date = local_dt.date()
    utc_dt = recorded_at.astimezone(timezone.utc)
    tz_name = timezone_name or getattr(tz, "key", "UTC")
    return utc_dt, local_date, tz_name
