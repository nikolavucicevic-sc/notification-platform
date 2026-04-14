from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from uuid import UUID
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models.notification import Notification, NotificationStatus, NotificationType
from app.models.user import User, UserRole
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.messaging.publisher import publish_email_request
from app.auth import get_current_user, require_operator_or_admin
from app.audit import log_notification_created

router = APIRouter(prefix="/notifications", tags=["notifications"], redirect_slashes=False)
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=NotificationResponse, status_code=201)
@limiter.limit("10/minute")
async def create_notification(
    request: Request,
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin)
):
    recipient_count = len(notification.customer_ids)
    channel = notification.notification_type

    # Enforce per-user sending limits (skip for SUPER_ADMIN)
    if current_user.role not in [UserRole.SUPER_ADMIN]:
        if channel == NotificationType.EMAIL and current_user.email_limit is not None:
            if current_user.email_sent + recipient_count > current_user.email_limit:
                remaining = max(0, current_user.email_limit - current_user.email_sent)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Email limit reached. Limit: {current_user.email_limit}, sent: {current_user.email_sent}, remaining: {remaining}"
                )
        if channel == NotificationType.SMS and current_user.sms_limit is not None:
            if current_user.sms_sent + recipient_count > current_user.sms_limit:
                remaining = max(0, current_user.sms_limit - current_user.sms_sent)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"SMS limit reached. Limit: {current_user.sms_limit}, sent: {current_user.sms_sent}, remaining: {remaining}"
                )

    db_notification = Notification(
        notification_type=notification.notification_type,
        subject=notification.subject,
        body=notification.body,
        customer_ids=[str(cid) for cid in notification.customer_ids],
        status=NotificationStatus.PENDING,
        created_by_user_id=current_user.id,
        tenant_id=current_user.tenant_id,
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    await publish_email_request(db_notification)
    db_notification.status = NotificationStatus.PROCESSING

    if channel == NotificationType.EMAIL:
        current_user.email_sent = (current_user.email_sent or 0) + recipient_count
    else:
        current_user.sms_sent = (current_user.sms_sent or 0) + recipient_count

    db.commit()
    db.refresh(db_notification)

    await log_notification_created(
        db=db, user=current_user,
        notification_id=str(db_notification.id),
        notification_type=db_notification.notification_type.value,
        customer_count=recipient_count,
        request=request
    )
    return db_notification


@router.patch("/{notification_id}/status", response_model=NotificationResponse)
async def update_notification_status(
    notification_id: UUID,
    status_data: dict,
    db: Session = Depends(get_db),
):
    """Internal endpoint — called by email-sender/sms-sender. No auth required."""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    status_str = status_data.get("status")
    try:
        notification.status = NotificationStatus[status_str]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status_str}")

    db.commit()
    db.refresh(notification)
    return notification


@router.get("", response_model=list[NotificationResponse])
async def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notifications. SUPER_ADMIN sees all. Others see only their tenant's notifications.
    """
    if current_user.role == UserRole.SUPER_ADMIN:
        return db.query(Notification).order_by(Notification.created_at.desc()).all()
    return (
        db.query(Notification)
        .filter(Notification.tenant_id == current_user.tenant_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


@router.get("/stats/summary")
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Notification stats broken down by status and channel."""
    base = db.query(Notification)
    if current_user.role != UserRole.SUPER_ADMIN:
        base = base.filter(Notification.tenant_id == current_user.tenant_id)

    total = base.count()
    by_status = {}
    for s in NotificationStatus:
        by_status[s.value.lower()] = base.filter(Notification.status == s).count()

    by_channel = {}
    for t in NotificationType:
        by_channel[t.value.lower()] = base.filter(Notification.notification_type == t).count()

    # Last 10 notifications for activity feed
    recent = base.order_by(Notification.created_at.desc()).limit(10).all()

    return {
        "total": total,
        "by_status": by_status,
        "by_channel": by_channel,
        "recent": [
            {
                "id": str(n.id),
                "type": n.notification_type.value,
                "status": n.status.value,
                "subject": n.subject,
                "recipient_count": len(n.customer_ids),
                "created_at": n.created_at.isoformat(),
            }
            for n in recent
        ],
    }


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # Ensure tenant isolation
    if current_user.role != UserRole.SUPER_ADMIN and notification.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification
