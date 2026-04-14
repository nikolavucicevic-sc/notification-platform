from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from app.schemas.user import UserResponse
from app.auth import get_password_hash, require_super_admin

router = APIRouter(prefix="/tenants", tags=["Tenants"], redirect_slashes=False)


@router.post("/", response_model=TenantResponse, status_code=201)
@router.post("", response_model=TenantResponse, status_code=201)
async def create_tenant(
    data: TenantCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_super_admin)
):
    """
    Create a new tenant and their first admin account. SUPER_ADMIN only.
    """
    if db.query(Tenant).filter(Tenant.name == data.name).first():
        raise HTTPException(status_code=400, detail="Tenant name already exists")

    if db.query(User).filter(User.username == data.admin_username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    if db.query(User).filter(User.email == data.admin_email).first():
        raise HTTPException(status_code=400, detail="Email already taken")

    # Create tenant
    tenant = Tenant(
        name=data.name,
        email_limit=data.email_limit,
        sms_limit=data.sms_limit,
    )
    db.add(tenant)
    db.flush()  # Get tenant.id before committing

    # Create tenant's first admin user
    admin_user = User(
        email=data.admin_email,
        username=data.admin_username,
        hashed_password=get_password_hash(data.admin_password),
        full_name=data.admin_full_name,
        role=UserRole.ADMIN,
        tenant_id=tenant.id,
    )
    db.add(admin_user)
    db.commit()
    db.refresh(tenant)

    tenant.user_count = db.query(User).filter(User.tenant_id == tenant.id).count()
    return tenant


@router.get("/", response_model=List[TenantResponse])
@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    db: Session = Depends(get_db),
    _: User = Depends(require_super_admin)
):
    """List all tenants with user counts. SUPER_ADMIN only."""
    tenants = db.query(Tenant).order_by(Tenant.created_at.desc()).all()
    for tenant in tenants:
        tenant.user_count = db.query(User).filter(User.tenant_id == tenant.id).count()
    return tenants


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_super_admin)
):
    """Get a single tenant. SUPER_ADMIN only."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.user_count = db.query(User).filter(User.tenant_id == tenant.id).count()
    return tenant


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    data: TenantUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_super_admin)
):
    """Update tenant name, limits, or active status. SUPER_ADMIN only."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if data.name is not None:
        existing = db.query(Tenant).filter(Tenant.name == data.name, Tenant.id != tenant_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tenant name already exists")
        tenant.name = data.name

    if data.is_active is not None:
        tenant.is_active = data.is_active

    # Allow setting limits to None (unlimited) explicitly
    if "email_limit" in data.model_fields_set:
        tenant.email_limit = data.email_limit
    if "sms_limit" in data.model_fields_set:
        tenant.sms_limit = data.sms_limit

    db.commit()
    db.refresh(tenant)
    tenant.user_count = db.query(User).filter(User.tenant_id == tenant.id).count()
    return tenant


@router.get("/{tenant_id}/users", response_model=List[UserResponse])
async def list_tenant_users(
    tenant_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_super_admin)
):
    """List all users in a tenant. SUPER_ADMIN only."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return db.query(User).filter(User.tenant_id == tenant_id).all()
