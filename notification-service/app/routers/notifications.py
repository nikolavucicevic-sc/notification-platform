from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models.notification import Notification, NotificationStatus
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.messaging.publisher import publish_email_request
from app.auth import get_current_user, require_operator_or_admin
from app.audit import log_notification_created

router = APIRouter(prefix="/notifications", tags=["notifications"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/", response_model=NotificationResponse, status_code=201)
@limiter.limit("10/minute")  # Max 10 notifications per minute per IP
async def create_notification(
    request: Request,
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin)  # Require auth
):
    """
    Create and send a notification with rate limiting (10 per minute per IP).

    Rate Limit: 10 requests per minute per IP address.
    Requires: OPERATOR or ADMIN role
    """
    db_notification = Notification(
        notification_type=notification.notification_type,
        subject=notification.subject,
        body=notification.body,
        customer_ids=[str(cid) for cid in notification.customer_ids],
        status=NotificationStatus.PENDING
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    await publish_email_request(db_notification)

    db_notification.status = NotificationStatus.PROCESSING
    db.commit()
    db.refresh(db_notification)

    # Audit log
    await log_notification_created(
        db=db,
        user=current_user,
        notification_id=str(db_notification.id),
        notification_type=db_notification.notification_type.value,
        customer_count=len(notification.customer_ids),
        request=request
    )

    return db_notification

@router.get("/", response_model=list[NotificationResponse])
async def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # All authenticated users can view
):
    """
    Get all notifications.
    Requires: Any authenticated user
    """
    return db.query(Notification).all()


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # All authenticated users can view
):
    """
    Get a specific notification by ID.
    Requires: Any authenticated user
    """
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


