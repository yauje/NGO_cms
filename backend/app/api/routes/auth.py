from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.core.config import settings
from app.core.permissions import get_role_permissions_verbose
from app.core.auth_deps import get_current_user, ALGORITHM
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.core.audit import record_audit_log

router = APIRouter(prefix="/auth", tags=["Authentication"])

ACCESS_TOKEN_EXPIRE_MINUTES = 15  # short-lived access token


# ==========================
# 🧍 ROUTES
# ==========================

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    permissions = get_role_permissions_verbose(current_user.role)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "permissions": permissions,
    }


@router.post("/register", response_model=UserRead)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await User.get_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(user_in.password)
    new_user = await User.create(
        db, email=user_in.email, hashed_password=hashed_pw, role=user_in.role
    )

    await record_audit_log(
        db=db,
        user=new_user,
        action="register",
        resource_type="user",
        resource_id=new_user.id,
    )

    return new_user


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=Token)
async def login_user(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return access + refresh tokens"""
    user = await User.get_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    # Issue tokens
    access_token = create_access_token(
        data={"sub": user.email, "id": user.id, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "id": user.id, "role": user.role}
    )

    # Store refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # set True in production
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )

    # Update last_token_issue for revocation
    user.last_token_issue = datetime.utcnow()
    db.add(user)
    await db.commit()

    await record_audit_log(
        db=db,
        user=user,
        action="login",
        resource_type="user",
        resource_id=user.id,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using HttpOnly refresh token"""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        token_iat = payload.get("iat")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = await User.get_by_email(db, email=email)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid user")

    if token_iat < user.last_token_issue.timestamp():
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    new_access_token = create_access_token(
        data={"sub": user.email, "id": user.id, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout_user(
    response: JSONResponse,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Logout user and revoke refresh tokens"""
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie("refresh_token")

    current_user.last_token_issue = datetime.utcnow()
    db.add(current_user)
    await db.commit()

    return response


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


@router.post("/reset-password/request")
async def request_password_reset(
    data: PasswordResetRequest, db: AsyncSession = Depends(get_db)
):
    user = await User.get_by_email(db, email=data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_access_token({"sub": user.email}, timedelta(minutes=30))

    # TODO: Send token via email in production instead of returning in response
    await record_audit_log(
        db=db,
        user=user,
        action="password_reset_request",
        resource_type="user",
        resource_id=user.id,
    )

    return {"message": "Password reset token generated", "reset_token": token}


@router.post("/reset-password/confirm")
async def confirm_password_reset(
    data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(data.token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = await User.get_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(data.new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await record_audit_log(
        db=db,
        user=user,
        action="password_reset_confirm",
        resource_type="user",
        resource_id=user.id,
    )

    # Revoke all refresh tokens on password change
    user.last_token_issue = datetime.utcnow()
    db.add(user)
    await db.commit()

    return {"message": "Password reset successful"}
