from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ... import analytics, schemas
from ...core.config import get_settings
from ...ml.recommender import recommendations_payload
from ...services.cache import get_json, set_json
from ...services.goals import list_goals
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


@router.get("/weekly-report", response_model=schemas.WeeklyReportResponse)
def weekly_report(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    from datetime import date, timedelta

    settings = get_settings()
    cache_key = f"weekly_report:{user.id}"
    cached = get_json(cache_key)
    if cached:
        return cached

    df = analytics.build_daily_dataframe(db, user_id=user.id)
    period_end = date.today()
    period_start = period_end - timedelta(days=6)
    if "date" in df.columns and not df.empty:
        df = df[(df["date"] >= period_start) & (df["date"] <= period_end)]
    payload = analytics.weekly_digest(df, period_start, period_end)
    cache_payload = {
        "period_start": payload["period_start"].isoformat(),
        "period_end": payload["period_end"].isoformat(),
        "summary": payload["summary"],
        "insight": payload["insight"],
        "generated_at": payload["generated_at"].isoformat(),
    }
    set_json(cache_key, cache_payload, settings.cache_ttl_seconds)
    return payload


@router.get("/recommendations", response_model=schemas.RecommendationsResponse)
def recommendations(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    settings = get_settings()
    cache_key = f"recommendations:{user.id}"
    cached = get_json(cache_key)
    if cached:
        return cached

    df = analytics.build_daily_dataframe(db, user_id=user.id)
    goals_objs = list_goals(db, user.id)
    goals = [
        {
            "sphere": g.sphere,
            "title": g.title,
            "target_value": g.target_value,
            "target_metric": g.target_metric,
        }
        for g in goals_objs
    ]
    payload = recommendations_payload(df, goals=goals)
    cache_payload = dict(payload)
    cache_payload["generated_at"] = payload["generated_at"].isoformat()
    set_json(cache_key, cache_payload, settings.cache_ttl_seconds)
    return payload


@router.get("/trend-this-month", response_model=schemas.TrendThisMonthResponse)
def trend_this_month(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    settings = get_settings()
    cache_key = f"trend_this_month:{user.id}"
    cached = get_json(cache_key)
    if cached:
        return cached

    df = analytics.build_daily_dataframe(db, user_id=user.id)
    metrics = analytics.trend_this_month(df)
    payload = {"metrics": metrics}
    set_json(cache_key, payload, settings.cache_ttl_seconds)
    return payload


@router.get("/insight-of-the-week", response_model=schemas.InsightOfTheWeekResponse)
def insight_of_the_week(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    settings = get_settings()
    cache_key = f"insight_of_the_week:{user.id}"
    cached = get_json(cache_key)
    if cached:
        return cached

    df = analytics.build_daily_dataframe(db, user_id=user.id)
    goals_objs = list_goals(db, user.id)
    goals = [
        {"sphere": g.sphere, "title": g.title, "target_value": g.target_value, "target_metric": g.target_metric}
        for g in goals_objs
    ]
    insight = analytics.insight_of_the_week(df, goals=goals)
    payload = {"insight": insight}
    set_json(cache_key, payload, settings.cache_ttl_seconds)
    return payload


@router.get("/weekday-trends", response_model=schemas.WeekdayTrendsResponse)
def weekday_trends(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    settings = get_settings()
    cache_key = f"weekday_trends:{user.id}"
    cached = get_json(cache_key)
    if cached:
        return cached

    df = analytics.build_daily_dataframe(db, user_id=user.id)
    payload = analytics.weekday_and_trends_payload(df)
    set_json(cache_key, payload, settings.cache_ttl_seconds)
    return payload
