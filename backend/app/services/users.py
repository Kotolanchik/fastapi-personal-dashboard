from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from .. import models
from ..core.constants import ROLE_USER
from ..core.security import hash_password, verify_password


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
) -> models.User:
    if full_name is not None:
        user.full_name = full_name
    if default_timezone is not None:
        user.default_timezone = default_timezone
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
