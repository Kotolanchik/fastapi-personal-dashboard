from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models import DataSource, SyncJob
from .registry import get_provider


def create_sync_job(db: Session, user_id: int, provider: str) -> SyncJob:
    job = SyncJob(
        user_id=user_id,
        provider=provider,
        status="queued",
        created_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def run_sync(db: Session, source: DataSource, settings=None) -> SyncJob:
    from ..core.config import get_settings
    settings = settings or get_settings()
    job = create_sync_job(db, source.user_id, source.provider)
    provider = get_provider(source.provider)
    job.started_at = datetime.now(timezone.utc)

    if not provider:
        job.status = "failed"
        job.message = "Provider not supported"
        if hasattr(source, "last_error"):
            source.last_error = job.message
    elif not provider.is_configured(source):
        job.status = "failed"
        job.message = "Integration not configured"
        if hasattr(source, "last_error"):
            source.last_error = job.message
    else:
        try:
            result = provider.fetch(source, db, settings=settings)
            job.status = result.status
            job.message = result.message
            job.stats = result.stats
            if result.status == "success":
                source.last_synced_at = datetime.now(timezone.utc)
                if hasattr(source, "last_error"):
                    source.last_error = None
            else:
                if hasattr(source, "last_error"):
                    source.last_error = result.message or result.status
        except Exception as e:
            job.status = "failed"
            job.message = str(e)[:500]
            if hasattr(source, "last_error"):
                source.last_error = job.message

    job.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job
