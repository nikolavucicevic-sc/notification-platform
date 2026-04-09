from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import secrets
import hashlib

from app.database import get_db
from app.models import User, APIKey, UserRole

# Security configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # TODO: Move to env var
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def generate_api_key() -> tuple[str, str, str]:
    full_key = f"npk_{secrets.token_hex(32)}"
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    key_prefix = full_key[:12]
    return full_key, key_hash, key_prefix


def verify_api_key(api_key: str, stored_hash: str) -> bool:
    computed_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return computed_hash == stored_hash


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Try JWT token first
    if not token.startswith("npk_"):
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            raise credentials_exception

        user.last_login = datetime.now(timezone.utc)
        db.commit()
        return user

    # Try API key
    key_prefix = token[:12]
    api_keys = db.query(APIKey).filter(
        APIKey.key_prefix == key_prefix,
        APIKey.is_active == True
    ).all()

    for api_key in api_keys:
        if verify_api_key(token, api_key.key_hash):
            if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key has expired"
                )
            api_key.last_used_at = datetime.now(timezone.utc)
            db.commit()

            user = db.query(User).filter(User.id == api_key.user_id).first()
            if user is None or not user.is_active:
                raise credentials_exception
            return user

    raise credentials_exception


def require_role(*allowed_roles: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


async def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require SUPER_ADMIN role — platform owner only."""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require ADMIN or SUPER_ADMIN role."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_operator_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require OPERATOR, ADMIN, or SUPER_ADMIN role."""
    if current_user.role not in [UserRole.OPERATOR, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator or Admin access required"
        )
    return current_user
