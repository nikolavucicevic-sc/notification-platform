import json
from app.database import settings
from app.models.notification import Notification
from app.redis_utils import RedisQueue


async def publish_email_request(notification: Notification):
    """
    Publish an email request to Redis queue.

    Redis Lists are used as a simple but effective message queue:
    - Producer pushes messages with LPUSH
    - Consumer blocks and pops with BRPOP
    - Much simpler than RabbitMQ, perfect for this use case
    """
    redis_queue = RedisQueue(settings.redis_url)

    try:
        message_body = {
            "notification_id": str(notification.id),
            "subject": notification.subject,
            "body": notification.body,
            "customer_ids": notification.customer_ids,
            "retry_count": 0
        }

        success = redis_queue.push(settings.redis_email_queue, message_body)

        if success:
            print(f"✓ Published email request for notification {notification.id} to Redis")
        else:
            print(f"✗ Failed to publish email request for notification {notification.id}")

    finally:
        redis_queue.close()
