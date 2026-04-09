import asyncio
import time

import requests

from app.config import settings
from app.services.sms_client import send_sms
from app.redis_utils import RedisQueue
from app.logging_config import get_logger

logger = get_logger(__name__)


def update_notification_status(notification_id: str, status: str):
    try:
        requests.patch(
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


async def process_sms_request(message: dict, redis_queue: RedisQueue):
    notification_id = message.get("notification_id")
    sms_body = message.get("body")
    customer_ids = message.get("customer_ids", [])
    retry_count = message.get("retry_count", 0)

    logger.info(
        "sms_processing_started",
        notification_id=notification_id,
        attempt=retry_count + 1,
        max_attempts=settings.max_retry_attempts + 1,
        customer_count=len(customer_ids)
    )

    try:
        for customer_id in customer_ids:
            result = await send_sms(customer_id, sms_body)
            logger.info(
                "sms_sent",
                notification_id=notification_id,
                customer_id=customer_id,
                phone_number=result.get("phone_number"),
                status=result.get("status")
            )

        logger.info("sms_processing_completed", notification_id=notification_id)
        update_notification_status(notification_id, "COMPLETED")

    except Exception as e:
        logger.error(
            "sms_processing_failed",
            notification_id=notification_id,
            attempt=retry_count + 1,
            error=str(e),
            exc_info=True
        )

        if retry_count < settings.max_retry_attempts:
            retry_count += 1
            backoff_seconds = settings.retry_backoff_base ** retry_count

            logger.info(
                "sms_retry_scheduled",
                notification_id=notification_id,
                retry=retry_count,
                max_retries=settings.max_retry_attempts,
                backoff_seconds=backoff_seconds
            )

            message["retry_count"] = retry_count
            message["last_error"] = str(e)
            message["last_attempt_at"] = time.time()

            await asyncio.sleep(backoff_seconds)
            redis_queue.push(settings.redis_sms_queue, message)

        else:
            logger.error(
                "sms_max_retries_exceeded",
                notification_id=notification_id,
                total_attempts=retry_count + 1
            )

            message["failed_at"] = time.time()
            message["failure_reason"] = str(e)
            message["total_attempts"] = retry_count + 1

            redis_queue.push(settings.redis_dlq_queue, message)
            update_notification_status(notification_id, "FAILED")


async def start_sms_consumer():
    redis_queue = RedisQueue(settings.redis_url)
    logger.info("sms_consumer_ready", queue=settings.redis_sms_queue)

    try:
        while True:
            message = redis_queue.pop(settings.redis_sms_queue, timeout=1)

            if message:
                try:
                    await process_sms_request(message, redis_queue)
                except Exception as e:
                    logger.error(
                        "sms_fatal_error",
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
        logger.info("sms_consumer_shutdown")
    except Exception as e:
        logger.error("sms_consumer_error", error=str(e), exc_info=True)
    finally:
        redis_queue.close()
