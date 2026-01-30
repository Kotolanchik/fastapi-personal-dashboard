"""Google Fit: OAuth + Fitness API (steps, activity) -> HealthEntry."""

from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

import requests

from ..models import DataSource, HealthEntry
from .base import IntegrationProvider, SyncResult


GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
FITNESS_SCOPES = [
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.body.read",
]
FITNESS_AGGREGATE_URL = "https://fitness.googleapis.com/fitness/v1/users/me/dataset:aggregate"


def get_oauth_url(client_id: str, redirect_uri: str, state: Optional[str] = None) -> str:
    scope = " ".join(FITNESS_SCOPES)
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "access_type": "offline",
        "prompt": "consent",
    }
    if state:
        params["state"] = state
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_OAUTH_AUTH_URL}?{qs}"


def exchange_code(
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> dict[str, Any]:
    resp = requests.post(
        GOOGLE_OAUTH_TOKEN_URL,
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> dict[str, Any]:
    resp = requests.post(
        GOOGLE_OAUTH_TOKEN_URL,
        data={
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _settings_include(source: DataSource, metric: str) -> bool:
    """Check if sync_settings allows this metric (default: all)."""
    settings = source.sync_settings or {}
    health = settings.get("health")
    if health is None:
        return True
    if isinstance(health, list) and "*" in health:
        return True
    return isinstance(health, list) and metric in health


def _fetch_steps(access_token: str, start_date: date, end_date: date) -> dict[date, int]:
    """Call Fitness API aggregate for steps; return dict local_date -> steps."""
    start_ts = int(datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc).timestamp() * 1000)
    end_ts = int(
        (datetime(end_date.year, end_date.month, end_date.day, tzinfo=timezone.utc) + timedelta(days=1)).timestamp()
        * 1000
    )
    body = {
        "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": str(start_ts),
        "endTimeMillis": str(end_ts),
    }
    resp = requests.post(
        FITNESS_AGGREGATE_URL,
        json=body,
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Fitness API error: {resp.status_code} {resp.text[:200]}")
    data = resp.json()
    result: dict[date, int] = {}
    for bucket in data.get("bucket", []):
        start_ms = int(bucket.get("startTimeMillis", 0))
        if not start_ms:
            continue
        local_date = date.fromtimestamp(start_ms / 1000.0)
        total = 0
        for ds in bucket.get("dataset", []):
            for point in ds.get("point", []):
                for val in point.get("value", []):
                    total += int(val.get("intVal", 0))
        result[local_date] = result.get(local_date, 0) + total
    return result


class GoogleFitProvider(IntegrationProvider):
    provider = "google_fit"

    def is_configured(self, source: DataSource) -> bool:
        return bool(source.access_token or source.refresh_token)

    def fetch(self, source: DataSource, db=None, settings=None) -> SyncResult:
        from sqlalchemy.orm import Session

        if not source.access_token and not source.refresh_token:
            return SyncResult(status="failed", message="No tokens", stats={})
        session: Session = db
        client_id = getattr(settings, "google_client_id", None) if settings else None
        client_secret = getattr(settings, "google_client_secret", None) if settings else None
        access_token = source.access_token
        if not client_id or not client_secret:
            return SyncResult(
                status="failed",
                message="Google OAuth not configured (GOOGLE_CLIENT_ID/SECRET)",
                stats={},
            )
        if source.refresh_token and (not access_token or self._token_expired(source)):
            try:
                tok = refresh_access_token(source.refresh_token, client_id, client_secret)
                access_token = tok.get("access_token")
                if access_token:
                    source.access_token = access_token
                    if "expires_in" in tok:
                        from datetime import datetime, timezone
                        source.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(tok["expires_in"]))
                    session.commit()
            except Exception as e:
                return SyncResult(status="failed", message=f"Token refresh failed: {e}", stats={})
        if not access_token:
            return SyncResult(status="failed", message="No access token", stats={})
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        try:
            steps_by_date = _fetch_steps(access_token, start_date, end_date)
        except Exception as e:
            return SyncResult(status="failed", message=str(e)[:500], stats={})
        if not _settings_include(source, "steps"):
            return SyncResult(status="success", message="Sync OK (steps disabled in settings)", stats={"days": 0})
        imported = 0
        tz_name = "UTC"
        for local_date, steps in steps_by_date.items():
            if steps <= 0:
                continue
            existing = (
                session.query(HealthEntry)
                .filter(
                    HealthEntry.user_id == source.user_id,
                    HealthEntry.local_date == local_date,
                )
                .first()
            )
            if existing:
                existing.steps = (existing.steps or 0) + steps
                imported += 1
            else:
                midnight_utc = datetime(local_date.year, local_date.month, local_date.day, tzinfo=timezone.utc)
                entry = HealthEntry(
                    user_id=source.user_id,
                    entry_type="day",
                    sleep_hours=0.0,
                    energy_level=5,
                    wellbeing=5,
                    steps=steps,
                    recorded_at=midnight_utc,
                    local_date=local_date,
                    timezone=tz_name,
                )
                session.add(entry)
                imported += 1
        session.commit()
        return SyncResult(
            status="success",
            message="OK",
            stats={"imported_records": imported, "days_with_steps": len(steps_by_date)},
        )

    def _token_expired(self, source: DataSource) -> bool:
        if not source.token_expires_at:
            return False
        from datetime import datetime, timezone
        return source.token_expires_at <= datetime.now(timezone.utc)
