# app/utils/security.py
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from app.config import settings
from app.services.database import get_database

# Setup HTTP Bearer authentication scheme
security = HTTPBearer()


async def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a new JWT access token.

    Args:
        data: Data to encode in the token.
        expires_delta: Optional expiration time.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.SECURITY.TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECURITY.SECRET_KEY, algorithm=settings.SECURITY.ALGORITHM)

    return encoded_jwt


async def verify_token(token: str):
    """Verify a JWT token.

    Args:
        token: JWT token to verify.

    Returns:
        dict: Decoded token payload.
    """
    try:
        payload = jwt.decode(token, settings.SECURITY.SECRET_KEY, algorithms=[settings.SECURITY.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_database)
):
    """Get the current authenticated user.

    Args:
        credentials: HTTP Bearer token credentials.
        db: Database connection.

    Returns:
        dict: User data.
    """
    token = credentials.credentials
    payload = await verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.users.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
