# backend/app/core/auth_deps.py

from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt, ExpiredSignatureError
from app.db.session import get_db
from app.db.models.user import User  # Assuming your custom method is here
from app.core.config import settings 

# ==========================
# 🔐 CONFIGURATION
# ==========================
# Use settings directly to ensure alignment with pydantic config
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login") # Adjusted tokenUrl for API prefix

# ==========================
# 🔧 DEPENDENCY (Enhanced)
# ==========================
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Extract and verify JWT token. 
    ENHANCEMENT: Checks token type and handles user retrieval safety.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # --- ENHANCEMENT 1: Token Type Verification ---
        token_type: str = payload.get("type")
        if token_type != "access":
            # Raised if a refresh token or an invalid type is presented
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token type, access token required"
            )

        email: str | None = payload.get("sub")
        
        # --- ENHANCEMENT 2: Safe None/Empty Check for Email ---
        if not email:
            raise credentials_exception
            
        # Optional: capture id and role if present
        user_id: int | None = payload.get("id")
        role: str | None = payload.get("role")
        
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except JWTError:
        raise credentials_exception

    # --- ENHANCEMENT 3: Assumes User.get_by_email is async (await added) and safe ---
    # User.get_by_email() is assumed to be an asynchronous class method 
    # defined on the User model that returns User or None.
    user = await User.get_by_email(db, email=email)
    
    # --- Safe handling of None from get_by_email() and is_active check ---
    if not user or not user.is_active:
        raise credentials_exception

    return user