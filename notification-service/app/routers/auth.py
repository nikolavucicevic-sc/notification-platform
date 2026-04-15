from datetime import datetime, timedelta, timezone
from typing import List
import hashlib
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, APIKey, AuditLog, PasswordResetToken
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
    ProfileUpdate,
)
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    require_admin,
    require_super_admin,
    generate_api_key
)
from app.audit import (
    log_user_login,
    log_api_key_created,
    log_user_created,
    create_audit_log
)

router = APIRouter(prefix="/auth", tags=["Authentication"], redirect_slashes=False)


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    # Block login if tenant is deactivated
    if user.tenant_id is not None:
        from app.models.tenant import Tenant
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if tenant and not tenant.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your organisation has been deactivated")

    access_token = create_access_token(data={"sub": str(user.id)})
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    await log_user_login(db=db, user=user, request=request)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Create a user within the current admin's tenant.
    Tenant admins can create OPERATOR and VIEWER only.
    SUPER_ADMIN cannot use this endpoint (use POST /tenants instead).
    """
    if admin.role == UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=400,
            detail="SUPER_ADMIN cannot create users directly. Use POST /tenants to create a tenant with its first admin."
        )

    # Tenant admins can only create OPERATOR or VIEWER
    if user_data.role not in [UserRole.OPERATOR, UserRole.VIEWER]:
        raise HTTPException(status_code=403, detail="Tenant admins can only create OPERATOR or VIEWER users")

    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        tenant_id=admin.tenant_id,  # Always inherit admin's tenant
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    await log_user_created(
        db=db, admin_user=admin,
        new_user_id=str(new_user.id),
        new_user_email=new_user.email,
        new_user_role=new_user.role.value,
        request=request
    )
    return new_user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    profile: ProfileUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if profile.full_name is not None:
        current_user.full_name = profile.full_name

    if profile.email is not None:
        existing = db.query(User).filter(User.email == profile.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = profile.email

    if profile.new_password is not None:
        if not profile.current_password:
            raise HTTPException(status_code=400, detail="Current password is required to set a new password")
        if not verify_password(profile.current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        current_user.hashed_password = get_password_hash(profile.new_password)

    db.commit()
    db.refresh(current_user)

    await create_audit_log(
        db=db, action="user.profile_update", user=current_user,
        resource_type="user", resource_id=str(current_user.id),
        details={"fields_updated": [f for f in ["full_name", "email", "password"] if getattr(profile, f if f != "password" else "new_password") is not None]},
        request=request
    )
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    List users. Tenant admins see only their own tenant's users.
    SUPER_ADMIN sees all users.
    """
    if admin.role == UserRole.SUPER_ADMIN:
        return db.query(User).all()
    return db.query(User).filter(User.tenant_id == admin.tenant_id).all()


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Tenant admin can only update users in their own tenant
    if admin.role != UserRole.SUPER_ADMIN and user.tenant_id != admin.tenant_id:
        raise HTTPException(status_code=403, detail="Cannot modify users outside your tenant")

    if user_update.email is not None:
        user.email = user_update.email
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.role is not None:
        # Tenant admin cannot assign ADMIN or SUPER_ADMIN
        if admin.role != UserRole.SUPER_ADMIN and user_update.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(status_code=403, detail="Cannot assign that role")
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
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if admin.role != UserRole.SUPER_ADMIN and user.tenant_id != admin.tenant_id:
        raise HTTPException(status_code=403, detail="Cannot modify users outside your tenant")

    role_str = role_data.get('role')
    allowed = ['ADMIN', 'OPERATOR', 'VIEWER'] if admin.role != UserRole.SUPER_ADMIN else ['ADMIN', 'OPERATOR', 'VIEWER', 'SUPER_ADMIN']
    if role_str not in allowed:
        raise HTTPException(status_code=400, detail="Invalid role")

    old_role = user.role.value
    user.role = UserRole[role_str]
    db.commit()
    db.refresh(user)

    await create_audit_log(
        db=db, action="user.role_update", user=admin,
        resource_type="user", resource_id=str(user.id),
        details={"old_role": old_role, "new_role": role_str},
        request=request
    )
    return user


@router.get("/users/me/usage", response_model=UserUsageResponse)
async def get_my_usage(current_user: User = Depends(get_current_user)):
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
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if admin.role != UserRole.SUPER_ADMIN and user.tenant_id != admin.tenant_id:
        raise HTTPException(status_code=403, detail="Cannot modify users outside your tenant")

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
        db=db, action="user.limits_update", user=admin,
        resource_type="user", resource_id=str(user.id),
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
    full_key, key_hash, key_prefix = generate_api_key()
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=key_data.expires_in_days)

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

    await log_api_key_created(
        db=db, user=current_user,
        api_key_id=str(api_key.id),
        key_name=key_data.key_name,
        request=request
    )
    return {"api_key": full_key, "key_info": api_key}


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(APIKey).filter(APIKey.user_id == current_user.id).all()


@router.delete("/api-keys/{key_id}", status_code=204)
async def delete_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    db.delete(api_key)
    db.commit()


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Audit logs scoped to tenant. SUPER_ADMIN sees all."""
    query = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    if admin.role != UserRole.SUPER_ADMIN:
        # Filter to only logs from users in this tenant
        tenant_user_ids = [
            str(u.id) for u in db.query(User).filter(User.tenant_id == admin.tenant_id).all()
        ]
        query = query.filter(AuditLog.user_id.in_(tenant_user_ids))
    return query.limit(limit).all()


@router.post("/password-reset/request", status_code=200)
async def request_password_reset(
    body: dict,
    db: Session = Depends(get_db),
):
    """
    Request a password reset token by email.
    Always returns 200 to avoid leaking whether an email is registered.
    The token is returned in the response for now (no email sending yet).
    """
    email = body.get("email", "").strip().lower()
    user = db.query(User).filter(User.email == email).first()

    # Don't leak whether the email exists
    if not user or not user.is_active:
        return {"message": "If that email is registered you will receive a reset token."}

    # Invalidate any previous unused tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False
    ).delete(synchronize_session=False)

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(reset_token)
    db.commit()

    # TODO: send raw_token via email when email-sending for platform users is wired up
    # For now return it directly so the flow is testable
    return {
        "message": "If that email is registered you will receive a reset token.",
        "reset_token": raw_token,   # Remove this line once email delivery is set up
    }


@router.post("/password-reset/confirm", status_code=200)
async def confirm_password_reset(
    body: dict,
    db: Session = Depends(get_db),
):
    """Consume a reset token and set a new password."""
    raw_token = body.get("token", "")
    new_password = body.get("new_password", "")

    if not raw_token or not new_password:
        raise HTTPException(status_code=400, detail="token and new_password are required")
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="new_password must be at least 8 characters")

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used == False,
    ).first()

    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if reset_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")

    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.hashed_password = get_password_hash(new_password)
    reset_token.used = True
    db.commit()

    return {"message": "Password updated successfully"}
