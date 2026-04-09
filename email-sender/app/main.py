import asyncio
from app.logging_config import configure_logging, get_logger
from app.messaging.consumer import start_email_consumer

configure_logging()
logger = get_logger(__name__)


async def main():
    logger.info("email_sender_starting", provider="configured via EMAIL_PROVIDER env var")
    await start_email_consumer()


if __name__ == "__main__":
    asyncio.run(main())
