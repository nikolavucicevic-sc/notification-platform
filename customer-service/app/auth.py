from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db, settings

ALGORITHM = "HS256"
security = HTTPBearer()


def get_current_tenant_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> tuple[str | None, str]:
    """
    Decode the JWT and return (tenant_id, user_role).
    tenant_id is None for SUPER_ADMIN.
    Raises 401 if token is invalid or user inactive.
    """
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise exc
    except JWTError:
        raise exc

    # Look up user in the shared DB (same Postgres instance)
    row = db.execute(
        text("SELECT tenant_id, role, is_active FROM users WHERE id = :uid"),
        {"uid": user_id}
    ).fetchone()

    if not row or not row.is_active:
        raise exc

    tenant_id = str(row.tenant_id) if row.tenant_id else None
    return tenant_id, row.role
