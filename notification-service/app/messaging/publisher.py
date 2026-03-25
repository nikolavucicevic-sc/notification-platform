import json
from app.database import settings
from app.models.notification import Notification, NotificationType
from app.redis_utils import RedisQueue


async def publish_email_request(notification: Notification):
    """
    Publish an email/SMS request to Redis queue.

    Redis Lists are used as a simple but effective message queue:
    - Producer pushes messages with LPUSH
    - Consumer blocks and pops with BRPOP
    - Much simpler than RabbitMQ, perfect for this use case

    Routes to different queues based on notification type:
    - EMAIL -> email_queue
    - SMS -> sms_queue
    """
    redis_queue = RedisQueue(settings.redis_url)

    try:
        message_body = {
            "notification_id": str(notification.id),
            "notification_type": notification.notification_type.value,
            "subject": notification.subject,
            "body": notification.body,
            "customer_ids": notification.customer_ids,
            "retry_count": 0
        }

        # Route to appropriate queue based on notification type
        if notification.notification_type == NotificationType.SMS:
            queue_name = settings.redis_sms_queue
        else:
            queue_name = settings.redis_email_queue

        success = redis_queue.push(queue_name, message_body)

        if success:
            print(f"✓ Published {notification.notification_type.value} request for notification {notification.id} to Redis queue: {queue_name}")
        else:
            print(f"✗ Failed to publish {notification.notification_type.value} request for notification {notification.id}")

    finally:
        redis_queue.close()
