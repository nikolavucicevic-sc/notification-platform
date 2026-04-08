from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, APIKey, AuditLog
from app.models.user import UserRole
from app.schemas.user import (
    UserLogin,
    UserCreate,
    UserResponse,
    Token,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyCreateResponse,
    AuditLogResponse,
    UserUpdate,
    UserLimitsUpdate,
    UserUsageResponse,
)
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    require_admin,
    generate_api_key
)
from app.audit import (
    log_user_login,
    log_api_key_created,
    log_user_created,
    create_audit_log
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Public self-registration endpoint. Creates new user with VIEWER role.
    """
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with VIEWER role (ignore any role from request for security)
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=UserRole.VIEWER  # Always VIEWER for self-registration
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Audit log (no admin user for self-registration)
    await log_user_created(
        db=db,
        admin_user=None,
        new_user_id=str(new_user.id),
        new_user_email=new_user.email,
        new_user_role=new_user.role.value,
        request=request
    )

    return new_user


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user_admin(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Create a new user (Admin only). Allows specifying role.
    """
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with specified role
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role  # Admin can specify role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Audit log
    await log_user_created(
        db=db,
        admin_user=admin,
        new_user_id=str(new_user.id),
        new_user_email=new_user.email,
        new_user_role=new_user.role.value,
        request=request
    )

    return new_user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login and receive a JWT access token.
    """
    # Find user
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Audit log
    await log_user_login(db=db, user=user, request=request)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    List all users (Admin only).
    """
    users = db.query(User).all()
    return users


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Update a user (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    db.commit()
    db.refresh(user)

    return user


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role_data: dict,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Update a user's role (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate role
    role_str = role_data.get('role')
    if role_str not in ['ADMIN', 'OPERATOR', 'VIEWER']:
        raise HTTPException(status_code=400, detail="Invalid role")

    old_role = user.role.value
    user.role = UserRole[role_str]

    db.commit()
    db.refresh(user)

    # Audit log
    await create_audit_log(
        db=db,
        action="user.role_update",
        user=admin,
        resource_type="user",
        resource_id=str(user.id),
        details={"old_role": old_role, "new_role": role_str},
        request=request
    )

    return user


@router.get("/users/me/usage", response_model=UserUsageResponse)
async def get_my_usage(current_user: User = Depends(get_current_user)):
    """
    Get the current user's notification usage and limits.
    Available to all authenticated users.
    """
    email_remaining = None
    sms_remaining = None
    if current_user.email_limit is not None:
        email_remaining = max(0, current_user.email_limit - (current_user.email_sent or 0))
    if current_user.sms_limit is not None:
        sms_remaining = max(0, current_user.sms_limit - (current_user.sms_sent or 0))

    return UserUsageResponse(
        email_limit=current_user.email_limit,
        sms_limit=current_user.sms_limit,
        email_sent=current_user.email_sent or 0,
        sms_sent=current_user.sms_sent or 0,
        email_remaining=email_remaining,
        sms_remaining=sms_remaining,
    )


@router.patch("/users/{user_id}/limits", response_model=UserResponse)
async def update_user_limits(
    user_id: str,
    limits: UserLimitsUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Set email/SMS sending limits for a user (Admin only).
    Pass null to remove a limit (unlimited).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if limits.email_limit is not None:
        user.email_limit = limits.email_limit
    elif "email_limit" in limits.model_fields_set:
        user.email_limit = None

    if limits.sms_limit is not None:
        user.sms_limit = limits.sms_limit
    elif "sms_limit" in limits.model_fields_set:
        user.sms_limit = None

    db.commit()
    db.refresh(user)

    await create_audit_log(
        db=db,
        action="user.limits_update",
        user=admin,
        resource_type="user",
        resource_id=str(user.id),
        details={"email_limit": user.email_limit, "sms_limit": user.sms_limit},
        request=request
    )

    return user


@router.post("/api-keys", response_model=APIKeyCreateResponse, status_code=201)
async def create_api_key(
    key_data: APIKeyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new API key for the current user.
    WARNING: The full API key is only shown once! Store it securely.
    """
    # Generate API key
    full_key, key_hash, key_prefix = generate_api_key()

    # Calculate expiration
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=key_data.expires_in_days)

    # Create API key record
    api_key = APIKey(
        user_id=current_user.id,
        key_name=key_data.key_name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        expires_at=expires_at
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    # Audit log
    await log_api_key_created(
        db=db,
        user=current_user,
        api_key_id=str(api_key.id),
        key_name=key_data.key_name,
        request=request
    )

    return {
        "api_key": full_key,  # Only shown once!
        "key_info": api_key
    }


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all API keys for the current user.
    """
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return api_keys


@router.delete("/api-keys/{key_id}", status_code=204)
async def delete_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete (revoke) an API key.
    """
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    db.delete(api_key)
    db.commit()

    return None


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    List audit logs (Admin only).
    Returns the most recent logs first.
    """
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return logs
