from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ... import models, schemas
from ...core.constants import ALLOWED_ROLES, ROLE_ADMIN
from ...services.users import set_user_role
from ..deps import get_db_session, require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[schemas.UserRead])
def list_users(
    db: Session = Depends(get_db_session),
    _admin=Depends(require_role(ROLE_ADMIN)),
):
    return db.query(models.User).order_by(models.User.id.asc()).all()


@router.put("/users/{user_id}/role", response_model=schemas.UserRead)
def update_user_role(
    user_id: int,
    payload: schemas.UserRoleUpdate,
    db: Session = Depends(get_db_session),
    _admin=Depends(require_role(ROLE_ADMIN)),
):
    if payload.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return set_user_role(db, user, payload.role)
