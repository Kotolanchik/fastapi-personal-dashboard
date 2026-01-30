from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ... import analytics, schemas
from ...core.config import get_settings
from ...services.cache import get_json, set_json
from ..deps import get_current_user, get_db_session

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/correlations", response_model=schemas.CorrelationsResponse)
def correlations(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    settings = get_settings()
    cache_key = f"correlations:{user.id}"
    cached = get_json(cache_key)
    if cached:
        return cached

    df = analytics.build_daily_dataframe(db, user_id=user.id)
    correlations_data = analytics.compute_correlations(df)
    payload = {"correlations": correlations_data}
    set_json(cache_key, payload, settings.cache_ttl_seconds)
    return payload


@router.get("/insights", response_model=schemas.InsightsResponse)
def insights(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    settings = get_settings()
    cache_key = f"insights:{user.id}"
    cached = get_json(cache_key)
    if cached:
        return cached

    payload = analytics.insights_payload(db, user_id=user.id)
    cache_payload = dict(payload)
    cache_payload["generated_at"] = payload["generated_at"].isoformat()
    set_json(cache_key, cache_payload, settings.cache_ttl_seconds)
    return payload
