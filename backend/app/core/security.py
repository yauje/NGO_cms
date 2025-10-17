from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# ==========================
# 🔐 PASSWORD CONTEXT
# ==========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = settings.ALGORITHM


# ==========================
# 🧩 PASSWORD HELPERS
# ==========================
def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

# ==========================
# 🎟️ TOKEN HELPERS
# ==========================
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a short-lived access token.
    Adds "type": "access" to ensure the token passes the type check in get_current_user.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a long-lived refresh token (default: 7 days) with iat for revocation."""
    iat = datetime.utcnow()
    expire = iat + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "iat": iat, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
