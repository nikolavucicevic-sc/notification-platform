import json
import aio_pika
from datetime import datetime

from app.config import settings
from app.services.email_client import send_email
from app.messaging.publisher import publish_status


MAX_RETRIES = 3
RETRY_DELAY = 60000  # 1 minute in milliseconds


async def process_dlq_message(message: aio_pika.IncomingMessage, channel: aio_pika.Channel):
    """Process messages from the dead-letter queue and retry if applicable."""
    try:
        body = json.loads(message.body.decode())
        print(f"Processing DLQ message: {body}")

        notification_id = body.get("notification_id")
        subject = body.get("subject")
        email_body = body.get("body")
        customer_ids = body.get("customer_ids")
        retry_count = body.get("retry_count", 0)

        # Check if we should retry
        if retry_count < MAX_RETRIES:
            print(f"Retrying notification {notification_id}, attempt {retry_count + 1}/{MAX_RETRIES}")

            try:
                # Attempt to send emails again
                results = []
                for customer_id in customer_ids:
                    result = await send_email(customer_id, subject, email_body)
                    results.append(result)
                    print(f"Email result for customer {customer_id}: {result}")

                # If successful, publish status and ack
                await publish_status(channel, notification_id, results)
                await message.ack()
                print(f"Successfully retried notification {notification_id}")

            except Exception as e:
                print(f"Retry failed for notification {notification_id}: {e}")

                # Increment retry count and republish to main queue
                body["retry_count"] = retry_count + 1

                main_queue = await channel.declare_queue(settings.rabbitmq_email_queue, durable=True)

                await channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(body).encode(),
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                        expiration=RETRY_DELAY  # Delay retry by 1 minute
                    ),
                    routing_key=main_queue.name
                )

                await message.ack()
                print(f"Requeued notification {notification_id} for retry {retry_count + 1}")

        else:
            # Max retries exceeded, mark as permanently failed
            print(f"Max retries exceeded for notification {notification_id}")

            await publish_status(channel, notification_id, [{
                "success": False,
                "error": f"Failed after {MAX_RETRIES} retry attempts"
            }])

            await message.ack()
            print(f"Permanently failed notification {notification_id}")

    except Exception as e:
        print(f"Error processing DLQ message: {e}")
        await message.reject(requeue=False)


async def start_dlq_consumer():
    """Start consuming messages from the dead-letter queue."""
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()

    await channel.set_qos(prefetch_count=10)

    dlq_name = f"{settings.rabbitmq_email_queue}.dlq"
    dlq = await channel.declare_queue(dlq_name, durable=True)

    # Consume with manual acknowledgment
    await dlq.consume(lambda message: process_dlq_message(message, channel), no_ack=False)

    print(f"DLQ handler started, listening on: {dlq_name}")

    return connection
