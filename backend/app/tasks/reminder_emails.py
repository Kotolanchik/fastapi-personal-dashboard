"""Send reminder emails to users who opted in. Run via cron or worker.

Usage (from repo root):
  DATABASE_URL=... SMTP_HOST=... SMTP_PORT=587 SMTP_USER=... SMTP_PASSWORD=... \\
  python -m backend.app.tasks.reminder_emails
"""

from datetime import date, timedelta
import logging
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .. import models
from ..core.config import get_settings
from ..database import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_reminders_for_user(db, user_id: int) -> list[dict]:
    """Return list of reminder items for user (same logic as GET /reminders)."""
    yesterday = date.today() - timedelta(days=1)
    health_yesterday = (
        db.query(models.HealthEntry)
        .filter(
            models.HealthEntry.user_id == user_id,
            models.HealthEntry.local_date == yesterday,
        )
        .limit(1)
        .first()
    )
    reminders = []
    if health_yesterday is None:
        reminders.append({
            "type": "health_yesterday",
            "message": "Fill health for yesterday.",
        })
    # Optional: "inactive N days" - check last entry across spheres
    last_health = (
        db.query(models.HealthEntry.local_date)
        .filter(models.HealthEntry.user_id == user_id)
        .order_by(models.HealthEntry.local_date.desc())
        .limit(1)
        .scalar()
    )
    last_finance = (
        db.query(models.FinanceEntry.local_date)
        .filter(models.FinanceEntry.user_id == user_id)
        .order_by(models.FinanceEntry.local_date.desc())
        .limit(1)
        .scalar()
    )
    last_any = max(
        d for d in [last_health, last_finance] if d is not None
    ) if (last_health or last_finance) else None
    if last_any and (date.today() - last_any).days > 3:
        reminders.append({
            "type": "inactive_days",
            "message": f"You haven't logged in {(date.today() - last_any).days} days. Log today?",
        })
    return reminders


def send_email(to_email: str, subject: str, body: str) -> bool:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP not configured; skipping send")
        return False
    from_addr = settings.smtp_from_email or settings.smtp_user
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr(("LifePulse Dashboard", from_addr))
    msg["To"] = to_email
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(from_addr, [to_email], msg.as_string())
        logger.info("Sent reminder email to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send email to %s: %s", to_email, e)
        return False


def run_reminder_emails() -> int:
    """Load users with email reminders enabled, compute reminders, send emails. Returns count sent."""
    import os
    database_url = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = Session()
    sent = 0
    try:
        users = (
            db.query(models.User)
            .filter(
                models.User.notification_email.isnot(None),
                models.User.notification_email != "",
            )
            .all()
        )
        for user in users:
            prefs = getattr(user, "notification_preferences", None) or {}
            if not prefs.get("email_reminders"):
                continue
            email = (user.notification_email or "").strip()
            if not email:
                continue
            reminders = get_reminders_for_user(db, user.id)
            if not reminders:
                continue
            subject = "LifePulse: Reminder"
            body = "Hi,\n\n" + "\n".join(r["message"] for r in reminders) + "\n\n— LifePulse Dashboard"
            if send_email(email, subject, body):
                sent += 1
    finally:
        db.close()
    return sent


if __name__ == "__main__":
    sent = run_reminder_emails()
    logger.info("Reminder emails sent: %s", sent)
