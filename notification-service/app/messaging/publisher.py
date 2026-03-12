import json
import aio_pika

from app.database import settings
from app.models.notification import Notification


async def publish_email_request(notification: Notification):
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)

    async with connection:
        channel = await connection.channel()

        # Declare dead-letter exchange and queue
        dlx_name = f"{settings.rabbitmq_email_queue}.dlx"
        dlq_name = f"{settings.rabbitmq_email_queue}.dlq"

        await channel.declare_exchange(dlx_name, aio_pika.ExchangeType.DIRECT, durable=True)
        await channel.declare_queue(dlq_name, durable=True)

        # Declare main queue with DLX configuration
        queue = await channel.declare_queue(
            settings.rabbitmq_email_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": dlx_name,
                "x-dead-letter-routing-key": dlq_name,
            }
        )

        message_body = {
            "notification_id": str(notification.id),
            "subject": notification.subject,
            "body": notification.body,
            "customer_ids": notification.customer_ids,
            "retry_count": 0
        }

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message_body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                expiration=300000  # 5 minutes timeout
            ),
            routing_key=queue.name
        )

        print(f"Published email request for notification {notification.id}")