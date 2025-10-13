# app/core/auth_deps.py

from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from app.db.session import get_db
from app.db.models.user import User
from app.core.config import settings # Assuming SECRET_KEY is here, otherwise define it

# ==========================
# 🔐 CONFIGURATION (Moved from auth.py)
# ==========================
# Use settings for real apps, but for this example, let's keep the hardcode if needed
SECRET_KEY = "a_very_secret_key_change_this"
ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES is only needed by create_access_token, leave it in auth.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ==========================
# 🔧 DEPENDENCY
# ==========================
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extract and verify JWT token to return the current authenticated User."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Use the correct SECRET_KEY
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Assuming User.get_by_email is defined on the User model
    user = await User.get_by_email(db, email=email)
    if user is None or not user.is_active:
        raise credentials_exception
    return user