from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.core.config import settings
from app.core.permissions import get_role_permissions_verbose
from app.core.auth_deps import get_current_user, SECRET_KEY, ALGORITHM
from app.core.audit import record_audit_log

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ==========================
# 🔐 CONFIGURATION
# ==========================
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================
# 🔧 HELPERS
# ==========================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ==========================
# 🧍 ROUTES
# ==========================

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Return current user info along with human-readable permissions"""
    permissions = get_role_permissions_verbose(current_user.role)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "permissions": permissions
    }

@router.post("/register", response_model=UserRead)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user account with audit logging"""
    existing_user = await User.get_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(user_in.password)
    new_user = await User.create(
        db, email=user_in.email, hashed_password=hashed_pw, role=user_in.role
    )

    # Audit log
    await record_audit_log(
        db=db,
        user=new_user,  # the newly created user
        action="register",
        resource_type="user",
        resource_id=new_user.id,
    )

    return new_user

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token with audit logging"""
    user = await User.get_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    access_token = create_access_token(data={"sub": user.email})

    # Audit log
    await record_audit_log(
        db=db,
        user=user,
        action="login",
        resource_type="user",
        resource_id=user.id,
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout_user(request: Request):
    """Logout endpoint (client-side token discard)"""
    return {"message": "Logout successful. Please discard your token."}

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@router.post("/reset-password/request")
async def request_password_reset(data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """Generate a password reset token with audit logging"""
    user = await User.get_by_email(db, email=data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_access_token({"sub": user.email}, timedelta(minutes=30))

    # Audit log
    await record_audit_log(
        db=db,
        user=user,
        action="password_reset_request",
        resource_type="user",
        resource_id=user.id,
    )

    return {"message": "Password reset token generated", "reset_token": token}

@router.post("/reset-password/confirm")
async def confirm_password_reset(data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    """Reset password using token with audit logging"""
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
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

    # Audit log
    await record_audit_log(
        db=db,
        user=user,
        action="password_reset_confirm",
        resource_type="user",
        resource_id=user.id,
    )

    return {"message": "Password reset successful"}
