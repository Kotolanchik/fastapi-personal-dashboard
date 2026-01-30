"""Apple Health: import from export XML (steps, sleep) -> HealthEntry."""

import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date, datetime, timezone
from io import BytesIO
from typing import Optional
import zipfile

from ..models import DataSource, HealthEntry
from .base import IntegrationProvider, SyncResult


# Apple Health export: Record type identifiers
STEP_TYPE = "HKQuantityTypeIdentifierStepCount"
SLEEP_TYPE = "HKCategoryTypeIdentifierSleepAnalysis"
HEART_RATE_TYPE = "HKQuantityTypeIdentifierHeartRate"
WEIGHT_TYPE = "HKQuantityTypeIdentifierBodyMass"


def _parse_apple_health_xml(content: bytes) -> tuple[dict[date, int], dict[date, float], dict[date, float], dict[date, float]]:
    """Parse export.xml; return steps_by_date, sleep_hours_by_date, heart_rate_by_date, weight_by_date."""
    steps_by_date: dict[date, int] = defaultdict(int)
    sleep_minutes_by_date: dict[date, float] = defaultdict(float)
    heart_rate_sum_count: dict[date, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    weight_by_date: dict[date, float] = {}  # last value per day

    root = ET.fromstring(content)
    # HealthData contains Record elements
    for record in root.findall(".//Record"):
        if record is None:
            continue
        kind = record.get("type")
        if not kind:
            continue
        start = record.get("startDate")
        end = record.get("endDate")
        value_str = record.get("value")
        if not start:
            continue
        try:
            local_date = date.fromisoformat(start[:10])
        except Exception:
            continue
        if kind == STEP_TYPE and value_str:
            try:
                steps_by_date[local_date] += int(float(value_str))
            except ValueError:
                pass
        elif kind == SLEEP_TYPE:
            # value 1=inBed, 2=asleep, etc.; use endDate - startDate for duration
            try:
                if end and start:
                    end_dt = datetime.strptime(end[:19].replace(" ", "T"), "%Y-%m-%dT%H:%M:%S")
                    start_dt = datetime.strptime(start[:19].replace(" ", "T"), "%Y-%m-%dT%H:%M:%S")
                    minutes = (end_dt - start_dt).total_seconds() / 60.0
                    sleep_minutes_by_date[local_date] += minutes
            except Exception:
                pass
        elif kind == HEART_RATE_TYPE and value_str:
            try:
                v = float(value_str)
                s, c = heart_rate_sum_count[local_date]
                heart_rate_sum_count[local_date] = (s + v, c + 1)
            except ValueError:
                pass
        elif kind == WEIGHT_TYPE and value_str:
            try:
                weight_by_date[local_date] = float(value_str)
            except ValueError:
                pass
    sleep_hours_by_date = {d: m / 60.0 for d, m in sleep_minutes_by_date.items()}
    heart_rate_by_date = {d: s / c if c else 0.0 for d, (s, c) in heart_rate_sum_count.items()}
    return steps_by_date, sleep_hours_by_date, heart_rate_by_date, weight_by_date


def _settings_include(source: Optional[DataSource], metric: str) -> bool:
    if not source:
        return True
    settings = getattr(source, "sync_settings", None) or {}
    health = settings.get("health")
    if health is None:
        return True
    if isinstance(health, list) and "*" in health:
        return True
    return isinstance(health, list) and metric in health


def map_apple_health_to_health_entries(
    db,
    user_id: int,
    steps_by_date: dict,
    sleep_hours_by_date: dict,
    heart_rate_by_date: dict,
    weight_by_date: dict,
    source: Optional[DataSource] = None,
) -> int:
    """Map parsed Apple Health data (by-date dicts) to HealthEntry: upsert per date. Returns count of records updated/created."""
    tz_name = "UTC"
    imported = 0
    all_dates = set(steps_by_date) | set(sleep_hours_by_date) | set(heart_rate_by_date) | set(weight_by_date)
    for local_date in all_dates:
        steps = steps_by_date.get(local_date, 0)
        sleep_hours = sleep_hours_by_date.get(local_date, 0.0)
        heart_rate = heart_rate_by_date.get(local_date)
        weight = weight_by_date.get(local_date)
        if not any([steps, sleep_hours, heart_rate is not None, weight is not None]):
            continue
        existing = (
            db.query(HealthEntry)
            .filter(HealthEntry.user_id == user_id, HealthEntry.local_date == local_date)
            .first()
        )
        midnight_utc = datetime(local_date.year, local_date.month, local_date.day, tzinfo=timezone.utc)
        if existing:
            if steps and _settings_include(source, "steps"):
                existing.steps = (existing.steps or 0) + steps
            if sleep_hours and _settings_include(source, "sleep"):
                existing.sleep_hours = max(existing.sleep_hours or 0, sleep_hours)
            if heart_rate is not None and _settings_include(source, "heart_rate"):
                existing.heart_rate_avg = int(heart_rate)
            if weight is not None and _settings_include(source, "weight"):
                existing.weight_kg = weight
            imported += 1
        else:
            entry = HealthEntry(
                user_id=user_id,
                entry_type="day",
                sleep_hours=sleep_hours if _settings_include(source, "sleep") else 0.0,
                energy_level=5,
                wellbeing=5,
                steps=steps if _settings_include(source, "steps") else None,
                heart_rate_avg=int(heart_rate) if heart_rate is not None and _settings_include(source, "heart_rate") else None,
                weight_kg=weight if _settings_include(source, "weight") else None,
                recorded_at=midnight_utc,
                local_date=local_date,
                timezone=tz_name,
            )
            db.add(entry)
            imported += 1
    db.commit()
    return imported


class AppleHealthProvider(IntegrationProvider):
    provider = "apple_health"

    def is_configured(self, source: DataSource) -> bool:
        return True  # No OAuth; import is file-based

    def fetch(self, source: DataSource, db=None, settings=None) -> SyncResult:
        return SyncResult(
            status="skipped",
            message="Use POST /integrations/apple-health/import with export.xml file.",
            stats={"imported_records": 0},
        )


def import_apple_health_xml(
    db,
    user_id: int,
    content: bytes,
    source: Optional[DataSource] = None,
    is_zip: bool = False,
) -> SyncResult:
    """Parse Apple Health export (XML or ZIP with export.xml) and upsert HealthEntry."""
    if is_zip:
        with zipfile.ZipFile(BytesIO(content), "r") as z:
            names = z.namelist()
            if "export.xml" in names:
                content = z.read("export.xml")
            else:
                for n in names:
                    if n.endswith(".xml"):
                        content = z.read(n)
                        break
                else:
                    return SyncResult(status="failed", message="No export.xml in ZIP", stats={})
    try:
        steps_by_date, sleep_hours_by_date, heart_rate_by_date, weight_by_date = _parse_apple_health_xml(content)
    except ET.ParseError as e:
        return SyncResult(status="failed", message=f"Invalid XML: {e}", stats={})
    imported = map_apple_health_to_health_entries(
        db, user_id,
        steps_by_date, sleep_hours_by_date, heart_rate_by_date, weight_by_date,
        source=source,
    )
    all_dates = set(steps_by_date) | set(sleep_hours_by_date) | set(heart_rate_by_date) | set(weight_by_date)
    return SyncResult(
        status="success",
        message="OK",
        stats={"imported_records": imported, "days": len(all_dates)},
    )
