import json
import asyncio
import time

from app.config import settings
from app.services.email_client import send_email
from app.redis_utils import RedisQueue


async def process_email_request(message: dict, redis_queue: RedisQueue):
    """
    Process an email request from the Redis queue with retry logic.

    Retry Strategy:
    - Attempt 1: Immediate
    - Attempt 2: 5 seconds delay (5^1)
    - Attempt 3: 25 seconds delay (5^2)
    - Attempt 4: 125 seconds delay (5^3)
    - After max retries: Move to Dead Letter Queue

    Args:
        message: Message dict from Redis queue
        redis_queue: Redis queue instance for retry/DLQ operations
    """
    try:
        notification_id = message.get("notification_id")
        subject = message.get("subject")
        email_body = message.get("body")
        customer_ids = message.get("customer_ids")
        retry_count = message.get("retry_count", 0)

        print(f"📨 Processing email notification {notification_id} (attempt {retry_count + 1}/{settings.max_retry_attempts + 1})")

        try:
            results = []
            for customer_id in customer_ids:
                result = await send_email(customer_id, subject, email_body)
                results.append(result)
                print(f"✓ Email sent to customer {customer_id}")

            print(f"✅ Successfully processed notification {notification_id}")

        except Exception as e:
            print(f"❌ Error processing notification {notification_id}: {e}")

            # Retry logic with exponential backoff
            if retry_count < settings.max_retry_attempts:
                retry_count += 1
                backoff_seconds = settings.retry_backoff_base ** retry_count

                print(f"⏱️  Scheduling retry {retry_count}/{settings.max_retry_attempts} in {backoff_seconds}s")

                # Update retry count in message
                message["retry_count"] = retry_count
                message["last_error"] = str(e)
                message["last_attempt_at"] = time.time()

                # Schedule retry by sleeping then re-queuing
                await asyncio.sleep(backoff_seconds)
                redis_queue.push(settings.redis_email_queue, message)

                print(f"🔄 Notification {notification_id} re-queued for retry")

            else:
                # Max retries exceeded - move to Dead Letter Queue
                print(f"💀 Max retries exceeded for notification {notification_id}, moving to DLQ")

                message["failed_at"] = time.time()
                message["failure_reason"] = str(e)
                message["total_attempts"] = retry_count + 1

                redis_queue.push(settings.redis_dlq_queue, message)
                print(f"📋 Notification {notification_id} moved to Dead Letter Queue")

    except Exception as e:
        print(f"✗ Fatal error processing message: {e}")
        # Move to DLQ if we can't even parse the message
        message["failed_at"] = time.time()
        message["failure_reason"] = f"Fatal error: {str(e)}"
        redis_queue.push(settings.redis_dlq_queue, message)


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
