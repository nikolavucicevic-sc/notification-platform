import asyncio
import time

import httpx

from app.config import settings
from app.services.email_client import send_email
from app.redis_utils import RedisQueue
from app.logging_config import get_logger

logger = get_logger(__name__)


async def update_notification_status(notification_id: str, status: str):
    try:
        async with httpx.AsyncClient() as client:
            await client.patch(
                f"{settings.notification_service_url}/notifications/{notification_id}/status",
                json={"status": status},
                timeout=5
            )
        logger.info("notification_status_updated", notification_id=notification_id, status=status)
    except Exception as e:
        logger.warning(
            "notification_status_update_failed",
            notification_id=notification_id,
            status=status,
            error=str(e)
        )


async def process_email_request(message: dict, redis_queue: RedisQueue):
    notification_id = message.get("notification_id")
    subject = message.get("subject")
    email_body = message.get("body")
    customer_ids = message.get("customer_ids", [])
    retry_count = message.get("retry_count", 0)

    logger.info(
        "email_processing_started",
        notification_id=notification_id,
        attempt=retry_count + 1,
        max_attempts=settings.max_retry_attempts + 1,
        customer_count=len(customer_ids)
    )

    try:
        for customer_id in customer_ids:
            result = await send_email(customer_id, subject, email_body)
            logger.info(
                "email_sent",
                notification_id=notification_id,
                customer_id=customer_id,
                success=result.get("success"),
                status_code=result.get("status_code")
            )

        logger.info("email_processing_completed", notification_id=notification_id)
        await update_notification_status(notification_id, "COMPLETED")

    except Exception as e:
        logger.error(
            "email_processing_failed",
            notification_id=notification_id,
            attempt=retry_count + 1,
            error=str(e),
            exc_info=True
        )

        if retry_count < settings.max_retry_attempts:
            retry_count += 1
            backoff_seconds = settings.retry_backoff_base ** retry_count

            logger.info(
                "email_retry_scheduled",
                notification_id=notification_id,
                retry=retry_count,
                max_retries=settings.max_retry_attempts,
                backoff_seconds=backoff_seconds
            )

            message["retry_count"] = retry_count
            message["last_error"] = str(e)
            message["last_attempt_at"] = time.time()

            await asyncio.sleep(backoff_seconds)
            redis_queue.push(settings.redis_email_queue, message)

        else:
            logger.error(
                "email_max_retries_exceeded",
                notification_id=notification_id,
                total_attempts=retry_count + 1
            )

            message["failed_at"] = time.time()
            message["failure_reason"] = str(e)
            message["total_attempts"] = retry_count + 1

            redis_queue.push(settings.redis_dlq_queue, message)
            await update_notification_status(notification_id, "FAILED")


async def start_email_consumer():
    redis_queue = RedisQueue(settings.redis_url)
    logger.info("email_consumer_ready", queue=settings.redis_email_queue)

    try:
        while True:
            message = redis_queue.pop(settings.redis_email_queue, timeout=1)

            if message:
                try:
                    await process_email_request(message, redis_queue)
                except Exception as e:
                    logger.error(
                        "email_fatal_error",
                        error=str(e),
                        message_keys=list(message.keys()),
                        exc_info=True
                    )
                    message["failed_at"] = time.time()
                    message["failure_reason"] = f"Fatal error: {str(e)}"
                    redis_queue.push(settings.redis_dlq_queue, message)
            else:
                await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("email_consumer_shutdown")
    except Exception as e:
        logger.error("email_consumer_error", error=str(e), exc_info=True)
    finally:
        redis_queue.close()
