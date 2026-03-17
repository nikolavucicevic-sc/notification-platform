import asyncio
from app.messaging.consumer import start_email_consumer
from app.messaging.dlq_handler import start_dlq_consumer
from app.config import settings
from app.rabbitmq_utils import wait_for_rabbitmq


async def main():
    print(f"Email Sender starting...")
    print(f"Listening on queue: {settings.rabbitmq_email_queue}")

    # Wait for RabbitMQ to be ready
    await wait_for_rabbitmq(settings.rabbitmq_url)

    # Start both main consumer and DLQ handler
    email_connection = await start_email_consumer()
    dlq_connection = await start_dlq_consumer()

    try:
        await asyncio.Future()
    finally:
        await email_connection.close()
        await dlq_connection.close()
        print("Email Sender stopped")


if __name__ == "__main__":
    asyncio.run(main())
