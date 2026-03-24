import json
import asyncio

from app.config import settings
from app.services.email_client import send_email
from app.redis_utils import RedisQueue


async def process_email_request(message: dict, redis_queue: RedisQueue):
    """
    Process an email request from the Redis queue.

    Args:
        message: Message dict from Redis queue
        redis_queue: Redis queue instance (not used for now, but here for future status updates)
    """
    try:
        print(f"Received email request: {message}")

        notification_id = message.get("notification_id")
        subject = message.get("subject")
        email_body = message.get("body")
        customer_ids = message.get("customer_ids")
        retry_count = message.get("retry_count", 0)

        try:
            results = []
            for customer_id in customer_ids:
                result = await send_email(customer_id, subject, email_body)
                results.append(result)
                print(f"✓ Email result for customer {customer_id}: {result}")

            print(f"✓ Successfully processed notification {notification_id}")

        except Exception as e:
            print(f"✗ Error processing notification {notification_id}: {e}")
            # With Redis, failed messages just get lost unless we add retry logic
            # For now, we just log the error. Could push to a "failed" queue if needed.

    except Exception as e:
        print(f"✗ Error decoding message: {e}")


async def start_email_consumer():
    """
    Start consuming email requests from Redis queue.

    This is simpler than RabbitMQ:
    - Create a RedisQueue
    - Loop forever
    - BRPOP blocks until a message arrives
    - Process the message
    - Repeat
    """
    redis_queue = RedisQueue(settings.redis_url)
    print(f"✓ Email Sender ready - listening on Redis queue: {settings.redis_email_queue}")

    try:
        while True:
            # BRPOP blocks until a message is available (timeout=1 second)
            message = redis_queue.pop(settings.redis_email_queue, timeout=1)

            if message:
                await process_email_request(message, redis_queue)
            else:
                # No message received within timeout, continue polling
                await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        print("\n✓ Shutting down email consumer...")
    except Exception as e:
        print(f"✗ Email consumer error: {e}")
    finally:
        redis_queue.close()
