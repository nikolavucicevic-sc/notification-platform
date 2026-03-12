import json
import aio_pika

from app.config import settings


async def publish_status(channel: aio_pika.Channel, notification_id: str, results: list[dict]):
    all_success = all(r["success"] for r in results)
    status = "COMPLETED" if all_success else "FAILED"

    message_body = {
        "notification_id": notification_id,
        "status": status,
        "results": results
    }

    queue = await channel.declare_queue(settings.rabbitmq_status_queue, durable=True)

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(message_body).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        ),
        routing_key=queue.name
    )

    print(f"Published status '{status}' for notification {notification_id}")
