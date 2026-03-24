import asyncio
from app.messaging.consumer import start_email_consumer
from app.config import settings
from app.redis_utils import wait_for_redis


async def main():
    print(f"Email Sender starting...")
    print(f"Listening on Redis queue: {settings.redis_email_queue}")

    # Wait for Redis to be ready
    wait_for_redis(settings.redis_url)

    # Start the email consumer (it will loop forever)
    await start_email_consumer()


if __name__ == "__main__":
    asyncio.run(main())
