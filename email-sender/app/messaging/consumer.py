import json
import aio_pika

from app.config import settings
from app.services.email_client import send_email
from app.messaging.publisher import publish_status


async def process_email_request(message: aio_pika.IncomingMessage, channel: aio_pika.Channel):
    try:
        body = json.loads(message.body.decode())
        print(f"Received email request: {body}")

        notification_id = body.get("notification_id")
        subject = body.get("subject")
        email_body = body.get("body")
        customer_ids = body.get("customer_ids")
        retry_count = body.get("retry_count", 0)

        try:
            results = []
            for customer_id in customer_ids:
                result = await send_email(customer_id, subject, email_body)
                results.append(result)
                print(f"Email result for customer {customer_id}: {result}")

            # Publish status update
            await publish_status(channel, notification_id, results)

            # Acknowledge message on success
            await message.ack()
            print(f"Successfully processed notification {notification_id}")

        except Exception as e:
            print(f"Error processing notification {notification_id}: {e}")

            # Reject message - it will go to DLQ
            await message.reject(requeue=False)

            # If message was rejected, publish FAILED status
            await publish_status(channel, notification_id, [{
                "success": False,
                "error": f"Processing failed: {str(e)}"
            }])

    except Exception as e:
        print(f"Error decoding message: {e}")
        # Reject malformed messages without requeue
        await message.reject(requeue=False)


async def start_email_consumer():
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()

    await channel.set_qos(prefetch_count=10)

    # Declare dead-letter exchange and queue
    dlx_name = f"{settings.rabbitmq_email_queue}.dlx"
    dlq_name = f"{settings.rabbitmq_email_queue}.dlq"

    await channel.declare_exchange(dlx_name, aio_pika.ExchangeType.DIRECT, durable=True)
    dlq = await channel.declare_queue(dlq_name, durable=True)
    await dlq.bind(dlx_name, routing_key=dlq_name)

    # Declare main queue with DLX configuration
    queue = await channel.declare_queue(
        settings.rabbitmq_email_queue,
        durable=True,
        arguments={
            "x-dead-letter-exchange": dlx_name,
            "x-dead-letter-routing-key": dlq_name,
        }
    )

    # Consume with manual acknowledgment
    await queue.consume(lambda message: process_email_request(message, channel), no_ack=False)

    print(f"Listening for email requests on queue: {settings.rabbitmq_email_queue}")
    print(f"Dead-letter queue configured: {dlq_name}")

    return connection