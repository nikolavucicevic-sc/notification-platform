from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models.notification import Notification, NotificationStatus
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.messaging.publisher import publish_email_request

router = APIRouter(prefix="/notifications", tags=["notifications"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/", response_model=NotificationResponse, status_code=201)
@limiter.limit("10/minute")  # Max 10 notifications per minute per IP
async def create_notification(
    request: Request,
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """
    Create and send a notification with rate limiting (10 per minute per IP).

    Rate Limit: 10 requests per minute per IP address.
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

    return db_notification

@router.get("/", response_model=list[NotificationResponse])
async def get_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).all()


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(notification_id: UUID, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


