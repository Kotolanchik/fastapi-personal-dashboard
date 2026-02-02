from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ... import models, schemas
from ...core.config import get_settings
from ...database import SessionLocal
from ...integrations.apple_health import import_apple_health_xml
from ...integrations.google_fit import exchange_code, get_oauth_url
from ...integrations.registry import list_providers
from ...integrations.sync import create_sync_job, run_sync
from ..deps import get_current_user, get_db_session

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/providers")
def providers():
    return {"providers": list_providers()}


@router.get("", response_model=list[schemas.DataSourceRead])
def list_sources(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    return (
        db.query(models.DataSource)
        .filter(models.DataSource.user_id == user.id)
        .order_by(models.DataSource.id.asc())
        .all()
    )


@router.get("/sources/{source_id}/status")
def get_source_status(
    source_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    """Source + last sync job (status, last error, «обновить сейчас» uses POST .../sync)."""
    source = (
        db.query(models.DataSource)
        .filter(models.DataSource.id == source_id, models.DataSource.user_id == user.id)
        .first()
    )
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    last_job = (
        db.query(models.SyncJob)
        .filter(
            models.SyncJob.user_id == user.id,
            models.SyncJob.provider == source.provider,
            models.SyncJob.data_source_id == source.id,
        )
        .order_by(models.SyncJob.created_at.desc())
        .limit(1)
        .first()
    )
    return {
        "source": schemas.DataSourceRead.model_validate(source),
        "last_job": schemas.SyncJobRead.model_validate(last_job) if last_job else None,
        "last_error": getattr(source, "last_error", None),
    }


@router.post("", response_model=schemas.DataSourceRead, status_code=201)
def connect_source(
    payload: schemas.DataSourceCreate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    existing = (
        db.query(models.DataSource)
        .filter(models.DataSource.user_id == user.id, models.DataSource.provider == payload.provider)
        .first()
    )
    now = datetime.now(timezone.utc)
    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else payload.dict(exclude_unset=True)
    metadata = data.pop("metadata", None)
    sync_settings = data.pop("sync_settings", None)
    if existing:
        if metadata is not None:
            existing.metadata_json = metadata
        if sync_settings is not None:
            existing.sync_settings = sync_settings
        for key, value in data.items():
            if key in ("metadata", "metadata_json"):
                continue
            setattr(existing, key, value)
        existing.updated_at = now
        db.commit()
        db.refresh(existing)
        return existing
    source = models.DataSource(
        user_id=user.id,
        provider=payload.provider,
        status=data.get("status", "connected"),
        access_token=data.get("access_token"),
        refresh_token=data.get("refresh_token"),
        token_expires_at=data.get("token_expires_at"),
        metadata_json=metadata,
        sync_settings=sync_settings,
        created_at=now,
        updated_at=now,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.put("/{source_id}", response_model=schemas.DataSourceRead)
def update_source(
    source_id: int,
    payload: schemas.DataSourceUpdate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    source = (
        db.query(models.DataSource)
        .filter(models.DataSource.id == source_id, models.DataSource.user_id == user.id)
        .first()
    )
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else payload.dict(exclude_unset=True)
    for key, value in data.items():
        if key == "metadata":
            setattr(source, "metadata_json", value)
        else:
            setattr(source, key, value)
    source.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(source)
    return source


@router.delete("/{source_id}", response_model=schemas.Message)
def delete_source(
    source_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    source = (
        db.query(models.DataSource)
        .filter(models.DataSource.id == source_id, models.DataSource.user_id == user.id)
        .first()
    )
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    db.delete(source)
    db.commit()
    return {"status": "deleted"}


# --- Google Fit OAuth ---

@router.get("/google_fit/oauth-url")
def google_fit_oauth_url(
    user=Depends(get_current_user),
):
    settings = get_settings()
    if not settings.google_client_id or not settings.google_redirect_uri:
        raise HTTPException(status_code=503, detail="Google OAuth not configured (GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URI)")
    state = str(user.id)  # optional: add nonce
    url = get_oauth_url(settings.google_client_id, settings.google_redirect_uri, state=state)
    return {"url": url}


@router.post("/google_fit/oauth-callback", response_model=schemas.DataSourceRead)
def google_fit_oauth_callback(
    body: schemas.OAuthCallbackBody,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    code = body.code
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret or settings.google_redirect_uri is None:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    try:
        tok = exchange_code(
            code,
            settings.google_client_id,
            settings.google_client_secret,
            settings.google_redirect_uri,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {e}")
    access_token = tok.get("access_token")
    refresh_token = tok.get("refresh_token")
    expires_in = tok.get("expires_in")
    token_expires_at = None
    if expires_in and access_token:
        token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
    existing = (
        db.query(models.DataSource)
        .filter(models.DataSource.user_id == user.id, models.DataSource.provider == "google_fit")
        .first()
    )
    now = datetime.now(timezone.utc)
    if existing:
        existing.access_token = access_token
        if refresh_token:
            existing.refresh_token = refresh_token
        existing.token_expires_at = token_expires_at
        existing.last_error = None
        existing.updated_at = now
        db.commit()
        db.refresh(existing)
        return existing
    source = models.DataSource(
        user_id=user.id,
        provider="google_fit",
        status="connected",
        access_token=access_token,
        refresh_token=refresh_token,
        token_expires_at=token_expires_at,
        created_at=now,
        updated_at=now,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


# --- Apple Health import (file) ---

@router.post("/apple-health/import")
def apple_health_import(
    file: UploadFile,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    """Import Apple Health export.xml (or ZIP containing export.xml)."""
    if not file.filename or not (file.filename.endswith(".xml") or file.filename.endswith(".zip")):
        raise HTTPException(status_code=400, detail="Upload export.xml or .zip from Health app")
    content = file.file.read()
    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 100MB)")
    is_zip = file.filename.endswith(".zip")
    source = (
        db.query(models.DataSource)
        .filter(models.DataSource.user_id == user.id, models.DataSource.provider == "apple_health")
        .first()
    )
    result = import_apple_health_xml(db, user.id, content, source=source, is_zip=is_zip)
    if result.status != "success":
        raise HTTPException(status_code=400, detail=result.message or result.status)
    return {"status": result.status, "message": result.message, "stats": result.stats}


# --- Sync (rate limit; run in background via BackgroundTasks) ---


def _execute_sync_background(source_id: int, job_id: int) -> None:
    """Run sync in background with a new DB session."""
    db = SessionLocal()
    try:
        source = db.query(models.DataSource).filter(models.DataSource.id == source_id).first()
        if not source:
            return
        job = db.query(models.SyncJob).filter(models.SyncJob.id == job_id).first()
        if not job:
            return
        run_sync(db, source, job=job)
    finally:
        db.close()


@router.post("/{provider}/sync", response_model=schemas.SyncJobRead)
def sync_provider(
    provider: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    source = (
        db.query(models.DataSource)
        .filter(models.DataSource.user_id == user.id, models.DataSource.provider == provider)
        .first()
    )
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    settings = get_settings()
    # Rate limit: min interval between syncs per source
    if source.last_synced_at and settings.sync_min_interval_seconds:
        if (datetime.now(timezone.utc) - source.last_synced_at).total_seconds() < settings.sync_min_interval_seconds:
            last_job = (
                db.query(models.SyncJob)
                .filter(
                    models.SyncJob.user_id == user.id,
                    models.SyncJob.provider == provider,
                    models.SyncJob.data_source_id == source.id,
                )
                .order_by(models.SyncJob.created_at.desc())
                .limit(1)
                .first()
            )
            if last_job:
                return last_job
    job = create_sync_job(db, user.id, provider, data_source_id=source.id)
    background_tasks.add_task(_execute_sync_background, source.id, job.id)
    return job


@router.get("/sync-jobs", response_model=list[schemas.SyncJobRead])
def list_sync_jobs(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    return (
        db.query(models.SyncJob)
        .filter(models.SyncJob.user_id == user.id)
        .order_by(models.SyncJob.created_at.desc())
        .limit(100)
        .all()
    )
