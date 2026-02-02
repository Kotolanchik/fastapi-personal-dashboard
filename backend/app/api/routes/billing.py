from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ... import models, schemas
from ...core.constants import ROLE_ADMIN
from ..deps import get_current_user, get_db_session, require_role

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans", response_model=list[schemas.PlanRead])
def list_plans(db: Session = Depends(get_db_session)):
    return (
        db.query(models.Plan)
        .filter(models.Plan.is_active == True)  # noqa: E712
        .order_by(models.Plan.price_monthly.asc())
        .all()
    )


@router.post("/plans", response_model=schemas.PlanRead, status_code=201)
def create_plan(
    payload: schemas.PlanCreate,
    db: Session = Depends(get_db_session),
    _admin=Depends(require_role(ROLE_ADMIN)),
):
    existing = db.query(models.Plan).filter(models.Plan.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=409, detail="Plan already exists")

    plan = models.Plan(
        code=payload.code,
        name=payload.name,
        price_monthly=payload.price_monthly,
        currency=payload.currency,
        is_active=payload.is_active,
        features=payload.features,
        created_at=datetime.now(timezone.utc),
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/subscribe", response_model=schemas.SubscriptionRead)
def subscribe(
    payload: schemas.SubscriptionCreate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    plan = db.get(models.Plan, payload.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(status_code=404, detail="Plan not available")

    active = (
        db.query(models.Subscription)
        .filter(models.Subscription.user_id == user.id, models.Subscription.status == "active")
        .first()
    )
    if active:
        active.status = "canceled"
        active.ends_at = datetime.now(timezone.utc)

    subscription = models.Subscription(
        user_id=user.id,
        plan_id=plan.id,
        status="active",
        started_at=datetime.now(timezone.utc),
        cancel_at_period_end=False,
        created_at=datetime.now(timezone.utc),
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


@router.get("/subscription", response_model=schemas.SubscriptionRead)
def current_subscription(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    subscription = (
        db.query(models.Subscription)
        .filter(models.Subscription.user_id == user.id)
        .order_by(models.Subscription.created_at.desc())
        .first()
    )
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    return subscription
