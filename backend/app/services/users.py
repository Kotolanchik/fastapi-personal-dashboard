import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from .. import models
from ..core.constants import ROLE_USER
from ..core.security import hash_password, verify_password

RESET_TOKEN_EXPIRE_HOURS = 24


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, email: str, password: str, full_name: Optional[str] = None):
    user = models.User(
        email=email.lower(),
        hashed_password=hash_password(password),
        full_name=full_name,
        created_at=datetime.now(timezone.utc),
        role=ROLE_USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email.lower())
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def set_user_role(db: Session, user: models.User, role: str) -> models.User:
    user.role = role
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(
    db: Session,
    user: models.User,
    *,
    full_name: Optional[str] = None,
    default_timezone: Optional[str] = None,
    dashboard_settings: Optional[dict] = None,
    notification_email: Optional[str] = None,
    notification_preferences: Optional[dict] = None,
) -> models.User:
    if full_name is not None:
        user.full_name = full_name
    if default_timezone is not None:
        user.default_timezone = default_timezone
    if dashboard_settings is not None:
        user.dashboard_settings = dashboard_settings
    if notification_email is not None:
        user.notification_email = notification_email
    if notification_preferences is not None:
        user.notification_preferences = notification_preferences
    db.commit()
    db.refresh(user)
    return user


def change_password(
    db: Session,
    user: models.User,
    current_password: str,
    new_password: str,
) -> Optional[models.User]:
    if not verify_password(current_password, user.hashed_password):
        return None
    user.hashed_password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def request_password_reset(db: Session, email: str) -> bool:
    """Set password_reset_token and password_reset_expires for user if exists. Returns True if user found."""
    user = get_user_by_email(db, email.lower())
    if not user:
        return False
    user.password_reset_token = secrets.token_urlsafe(32)
    user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
    db.commit()
    return True


def reset_password_by_token(db: Session, token: str, new_password: str) -> bool:
    """Find user by valid token, set new password, clear token. Returns True if success."""
    user = (
        db.query(models.User)
        .filter(
            models.User.password_reset_token == token,
            models.User.password_reset_expires.isnot(None),
            models.User.password_reset_expires > datetime.now(timezone.utc),
        )
        .first()
    )
    if not user:
        return False
    user.hashed_password = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.commit()
    db.refresh(user)
    return True
