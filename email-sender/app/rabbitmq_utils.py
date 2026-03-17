"""
RabbitMQ utilities for handling connection retries and ensuring
RabbitMQ availability during container startup.
"""
import asyncio
import sys
import aio_pika


async def wait_for_rabbitmq(rabbitmq_url: str, max_retries: int = 30, retry_interval: int = 2):
    """
    Wait for RabbitMQ to become available.

    Args:
        rabbitmq_url: RabbitMQ connection URL
        max_retries: Maximum number of connection attempts
        retry_interval: Seconds to wait between retries

    Raises:
        SystemExit: If RabbitMQ is not available after max_retries
    """
    print(f"Waiting for RabbitMQ to become available...")

    for attempt in range(1, max_retries + 1):
        try:
            # Try to establish a connection
            connection = await aio_pika.connect_robust(
                rabbitmq_url,
                timeout=5
            )
            print(f"✓ RabbitMQ connection established on attempt {attempt}")
            await connection.close()
            return
        except Exception as e:
            if attempt == max_retries:
                print(f"✗ Failed to connect to RabbitMQ after {max_retries} attempts")
                print(f"Error: {e}")
                sys.exit(1)

            print(f"Attempt {attempt}/{max_retries}: RabbitMQ not ready, retrying in {retry_interval}s...")
            print(f"  Error: {e}")
            await asyncio.sleep(retry_interval)