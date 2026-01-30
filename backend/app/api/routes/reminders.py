"""Reminders API: e.g. 'fill health for yesterday'."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ... import models
from ..deps import get_current_user, get_db_session

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("")
def list_reminders(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    """Returns list of reminder items (e.g. fill health for yesterday). Frontend can use to show modals or banners."""
    yesterday = date.today() - timedelta(days=1)
    health_yesterday = (
        db.query(models.HealthEntry)
        .filter(
            models.HealthEntry.user_id == user.id,
            models.HealthEntry.local_date == yesterday,
        )
        .limit(1)
        .first()
    )
    reminders = [
        {
            "type": "health_yesterday",
            "should_remind": health_yesterday is None,
            "message": "Fill health for yesterday.",
        },
    ]
    return {"reminders": reminders}
