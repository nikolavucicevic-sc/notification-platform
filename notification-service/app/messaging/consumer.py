import json
import aio_pika

from app.database import settings, SessionLocal
from app.models.notification import Notification, NotificationStatus


async def process_status_update(message: aio_pika.IncomingMessage):
    try:
        body = json.loads(message.body.decode())
        print(f"Received status update: {body}")

        notification_id = body.get("notification_id")
        status = body.get("status")

        if not notification_id or not status:
            print(f"Invalid status update message: {body}")
            await message.reject(requeue=False)
            return

        db = SessionLocal()
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()

            if not notification:
                print(f"Notification {notification_id} not found")
                await message.ack()  # Ack anyway, notification might have been deleted
                return

            # Update status
            notification.status = NotificationStatus[status]
            db.commit()
            print(f"Updated notification {notification_id} status to {status}")

            await message.ack()

        except Exception as e:
            print(f"Error updating notification {notification_id}: {e}")
            db.rollback()
            # Reject with requeue to retry later
            await message.reject(requeue=True)
        finally:
            db.close()

    except Exception as e:
        print(f"Error processing status update: {e}")
        await message.reject(requeue=False)


async def start_status_consumer():
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()

    await channel.set_qos(prefetch_count=10)

    queue = await channel.declare_queue(settings.rabbitmq_status_queue, durable=True)

    # Consume with manual acknowledgment
    await queue.consume(process_status_update, no_ack=False)

    print(f"Listening for status updates on queue: {settings.rabbitmq_status_queue}")

    return connection