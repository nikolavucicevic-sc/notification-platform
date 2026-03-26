from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
import redis
import json

from app.database import settings, get_db
from app.models.user import User
from app.auth import get_current_user, require_operator_or_admin, require_admin
from app.audit import log_dlq_retry, log_dlq_clear

router = APIRouter(prefix="/dlq", tags=["dlq"])


@router.get("/")
async def get_dlq_messages(
    current_user: User = Depends(get_current_user)  # All authenticated users
):
    """
    Get all messages from Dead Letter Queues (both email and SMS).
    Returns failed notifications for review and manual retry.
    """
    try:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)

        # Get all failed email messages
        email_dlq_messages = []
        email_dlq_length = redis_client.llen("email:dlq")
        for i in range(email_dlq_length):
            message_json = redis_client.lindex("email:dlq", i)
            if message_json:
                message = json.loads(message_json)
                message["channel"] = "EMAIL"
                message["dlq_index"] = i
                email_dlq_messages.append(message)

        # Get all failed SMS messages
        sms_dlq_messages = []
        sms_dlq_length = redis_client.llen("sms:dlq")
        for i in range(sms_dlq_length):
            message_json = redis_client.lindex("sms:dlq", i)
            if message_json:
                message = json.loads(message_json)
                message["channel"] = "SMS"
                message["dlq_index"] = i
                sms_dlq_messages.append(message)

        redis_client.close()

        return {
            "email_dlq": {
                "count": email_dlq_length,
                "messages": email_dlq_messages
            },
            "sms_dlq": {
                "count": sms_dlq_length,
                "messages": sms_dlq_messages
            },
            "total_failed": email_dlq_length + sms_dlq_length
        }

    except Exception as e:
        return {
            "error": str(e),
            "email_dlq": {"count": 0, "messages": []},
            "sms_dlq": {"count": 0, "messages": []},
            "total_failed": 0
        }


@router.post("/retry/{channel}/{notification_id}")
async def retry_dlq_message(
    channel: str,
    notification_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator_or_admin)  # Operator or Admin
):
    """
    Retry a specific failed notification by moving it back to the main queue.

    Args:
        channel: "email" or "sms"
        notification_id: The notification ID to retry

    Requires: OPERATOR or ADMIN role
    """
    try:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)

        dlq_name = f"{channel.lower()}:dlq"
        target_queue = settings.redis_email_queue if channel.upper() == "EMAIL" else settings.redis_sms_queue

        # Find and remove the message from DLQ
        dlq_length = redis_client.llen(dlq_name)
        message_found = None

        for i in range(dlq_length):
            message_json = redis_client.lindex(dlq_name, i)
            if message_json:
                message = json.loads(message_json)
                if message.get("notification_id") == notification_id:
                    message_found = message
                    # Remove from DLQ by value
                    redis_client.lrem(dlq_name, 1, message_json)
                    break

        if not message_found:
            redis_client.close()
            return {
                "success": False,
                "message": f"Notification {notification_id} not found in {channel} DLQ"
            }

        # Reset retry count and re-queue
        message_found["retry_count"] = 0
        message_found.pop("failed_at", None)
        message_found.pop("failure_reason", None)
        message_found.pop("total_attempts", None)

        redis_client.lpush(target_queue, json.dumps(message_found))
        redis_client.close()

        # Audit log
        await log_dlq_retry(
            db=db,
            user=current_user,
            notification_id=notification_id,
            channel=channel,
            request=request
        )

        return {
            "success": True,
            "message": f"Notification {notification_id} moved back to {target_queue}",
            "notification_id": notification_id
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error retrying notification: {str(e)}"
        }


@router.delete("/clear/{channel}")
async def clear_dlq(
    channel: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Admin only
):
    """
    Clear all messages from a specific DLQ (email or sms).

    Args:
        channel: "email" or "sms"

    Requires: ADMIN role
    """
    try:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        dlq_name = f"{channel.lower()}:dlq"

        count = redis_client.llen(dlq_name)
        redis_client.delete(dlq_name)
        redis_client.close()

        # Audit log
        await log_dlq_clear(
            db=db,
            user=current_user,
            channel=channel,
            count=count,
            request=request
        )

        return {
            "success": True,
            "message": f"Cleared {count} messages from {channel} DLQ"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error clearing DLQ: {str(e)}"
        }
