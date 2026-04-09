from app.config import settings
from app.services.email_client import send_email
from app.redis_utils import RedisQueue
from app.logging_config import get_logger

logger = get_logger(__name__)

MAX_RETRIES = 3


async def publish_status(notification_id: str, results: list[dict]):
    """Update notification status via the notification service."""
    from app.messaging.consumer import update_notification_status
    all_success = all(r.get("success", False) for r in results)
    status = "COMPLETED" if all_success else "FAILED"
    await update_notification_status(notification_id, status)


async def process_dlq_message(message: dict, redis_queue: RedisQueue):
    """Process messages from the dead-letter queue and retry if applicable."""
    notification_id = message.get("notification_id")
    subject = message.get("subject")
    email_body = message.get("body")
    customer_ids = message.get("customer_ids", [])
    retry_count = message.get("retry_count", 0)

    if retry_count < MAX_RETRIES:
        logger.info("dlq_retry_attempt", notification_id=notification_id,
                    attempt=retry_count + 1, max_retries=MAX_RETRIES)
        try:
            results = []
            for customer_id in customer_ids:
                result = await send_email(customer_id, subject, email_body)
                results.append(result)

            await publish_status(notification_id, results)
            logger.info("dlq_retry_success", notification_id=notification_id)

        except Exception as e:
            logger.warning("dlq_retry_failed", notification_id=notification_id,
                           attempt=retry_count + 1, error=str(e))
            message["retry_count"] = retry_count + 1
            redis_queue.push(settings.redis_email_queue, message)

    else:
        logger.error("dlq_max_retries_exceeded", notification_id=notification_id,
                     total_attempts=retry_count)
        await publish_status(notification_id, [{
            "success": False,
            "error": f"Failed after {MAX_RETRIES} retry attempts"
        }])


async def start_dlq_consumer():
    """Start consuming messages from the dead-letter queue."""
    redis_queue = RedisQueue(settings.redis_url)
    logger.info("dlq_consumer_ready", queue=settings.redis_dlq_queue)

    try:
        import asyncio
        while True:
            message = redis_queue.pop(settings.redis_dlq_queue, timeout=1)
            if message:
                try:
                    await process_dlq_message(message, redis_queue)
                except Exception as e:
                    logger.error("dlq_fatal_error", error=str(e), exc_info=True)
            else:
                await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("dlq_consumer_shutdown")
    finally:
        redis_queue.close()
