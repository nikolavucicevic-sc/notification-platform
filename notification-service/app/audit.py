from typing import Optional, Any
from sqlalchemy.orm import Session
from fastapi import Request
from datetime import datetime, timezone

from app.models import AuditLog, User


async def create_audit_log(
    db: Session,
    action: str,
    user: Optional[User] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
    request: Optional[Request] = None
):
    """
    Create an audit log entry.

    Args:
        db: Database session
        action: Action performed (e.g., "notification.create", "user.login", "dlq.retry")
        user: User who performed the action (optional for system actions)
        resource_type: Type of resource affected (e.g., "notification", "user")
        resource_id: ID of the affected resource
        details: Additional context as a dictionary
        request: FastAPI request object to extract IP and user agent
    """
    ip_address = None
    user_agent = None

    if request:
        # Extract IP address (handles proxies)
        if "x-forwarded-for" in request.headers:
            ip_address = request.headers["x-forwarded-for"].split(",")[0].strip()
        elif "x-real-ip" in request.headers:
            ip_address = request.headers["x-real-ip"]
        else:
            ip_address = request.client.host if request.client else None

        # Extract user agent
        user_agent = request.headers.get("user-agent")

    audit_entry = AuditLog(
        user_id=user.id if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.now(timezone.utc)
    )

    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)

    return audit_entry


# Convenience functions for common actions
async def log_notification_created(
    db: Session,
    user: User,
    notification_id: str,
    notification_type: str,
    customer_count: int,
    request: Request
):
    """Log notification creation."""
    await create_audit_log(
        db=db,
        action="notification.create",
        user=user,
        resource_type="notification",
        resource_id=notification_id,
        details={
            "notification_type": notification_type,
            "customer_count": customer_count
        },
        request=request
    )


async def log_user_login(db: Session, user: User, request: Request):
    """Log user login."""
    await create_audit_log(
        db=db,
        action="user.login",
        user=user,
        resource_type="user",
        resource_id=str(user.id),
        request=request
    )


async def log_dlq_retry(
    db: Session,
    user: User,
    notification_id: str,
    channel: str,
    request: Request
):
    """Log DLQ message retry."""
    await create_audit_log(
        db=db,
        action="dlq.retry",
        user=user,
        resource_type="notification",
        resource_id=notification_id,
        details={"channel": channel},
        request=request
    )


async def log_dlq_clear(
    db: Session,
    user: User,
    channel: str,
    count: int,
    request: Request
):
    """Log DLQ clear operation."""
    await create_audit_log(
        db=db,
        action="dlq.clear",
        user=user,
        resource_type="dlq",
        resource_id=channel,
        details={"messages_cleared": count},
        request=request
    )


async def log_api_key_created(
    db: Session,
    user: User,
    api_key_id: str,
    key_name: str,
    request: Request
):
    """Log API key creation."""
    await create_audit_log(
        db=db,
        action="api_key.create",
        user=user,
        resource_type="api_key",
        resource_id=api_key_id,
        details={"key_name": key_name},
        request=request
    )


async def log_user_created(
    db: Session,
    admin_user: Optional[User],
    new_user_id: str,
    new_user_email: str,
    new_user_role: str,
    request: Request
):
    """Log user creation. admin_user can be None for self-registration."""
    await create_audit_log(
        db=db,
        action="user.create",
        user=admin_user,
        resource_type="user",
        resource_id=new_user_id,
        details={"email": new_user_email, "role": new_user_role},
        request=request
    )
