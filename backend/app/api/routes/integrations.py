from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ... import models, schemas
from ...integrations.registry import list_providers
from ...integrations.sync import run_sync
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
    if existing:
        existing.status = payload.status or existing.status
        existing.access_token = payload.access_token or existing.access_token
        existing.refresh_token = payload.refresh_token or existing.refresh_token
        existing.token_expires_at = payload.token_expires_at or existing.token_expires_at
        existing.metadata_json = payload.metadata or existing.metadata_json
        existing.updated_at = now
        db.commit()
        db.refresh(existing)
        return existing

    source = models.DataSource(
        user_id=user.id,
        provider=payload.provider,
        status=payload.status or "connected",
        access_token=payload.access_token,
        refresh_token=payload.refresh_token,
        token_expires_at=payload.token_expires_at,
        metadata_json=payload.metadata,
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

    data = payload.dict(exclude_unset=True)
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


@router.post("/{provider}/sync", response_model=schemas.SyncJobRead)
def sync_provider(
    provider: str,
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
    job = run_sync(db, source)
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
