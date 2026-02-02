from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ... import schemas
from ...core.security import create_access_token
from ...services.users import (
    authenticate_user,
    change_password as change_password_service,
    create_user,
    get_user_by_email,
    request_password_reset,
    reset_password_by_token,
    update_user_profile,
)
from ..deps import get_current_user, get_db_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserRead, status_code=201)
def register_user(payload: schemas.UserCreate, db: Session = Depends(get_db_session)):
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = create_user(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )
    return user


@router.post("/login", response_model=schemas.Token)
def login_user(payload: schemas.UserLogin, db: Session = Depends(get_db_session)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login")
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserRead)
def read_current_user(user=Depends(get_current_user)):
    return user


@router.patch("/me", response_model=schemas.UserRead)
def update_profile(
    payload: schemas.UserProfileUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else payload.dict(exclude_unset=True)
    updated = update_user_profile(db, user, **data)
    return updated


@router.post("/change-password", status_code=204)
def change_password(
    payload: schemas.ChangePassword,
    user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    updated = change_password_service(
        db, user, payload.current_password, payload.new_password
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )


@router.post("/forgot-password", status_code=204)
def forgot_password(
    payload: schemas.ForgotPasswordRequest,
    db: Session = Depends(get_db_session),
):
    """Request password reset: sends no email; token is returned for demo/testing or via separate email service."""
    request_password_reset(db, payload.email)
    # Always 204 to avoid email enumeration


@router.post("/reset-password", status_code=204)
def reset_password(
    payload: schemas.ResetPasswordRequest,
    db: Session = Depends(get_db_session),
):
    updated = reset_password_by_token(db, payload.token, payload.new_password)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
