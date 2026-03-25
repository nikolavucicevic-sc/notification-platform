"""
Redis utilities for handling connection retries and message queue operations.
Redis is much lighter than RabbitMQ and perfect for simple message queuing.
"""
import time
import sys
import json
import redis
from typing import Dict, Any


def wait_for_redis(redis_url: str, max_retries: int = 30, retry_interval: int = 2):
    """
    Wait for Redis to become available.

    Args:
        redis_url: Redis connection URL
        max_retries: Maximum number of connection attempts
        retry_interval: Seconds to wait between retries

    Raises:
        SystemExit: If Redis is not available after max_retries
    """
    print(f"Waiting for Redis to become available...")

    for attempt in range(1, max_retries + 1):
        try:
            # Try to establish a connection
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            print(f"✓ Redis connection established on attempt {attempt}")
            client.close()
            return
        except Exception as e:
            if attempt == max_retries:
                print(f"✗ Failed to connect to Redis after {max_retries} attempts")
                print(f"Error: {e}")
                sys.exit(1)

            print(f"Attempt {attempt}/{max_retries}: Redis not ready, retrying in {retry_interval}s...")
            print(f"  Error: {e}")
            time.sleep(retry_interval)


class RedisQueue:
    """
    Simple Redis-based message queue using LIST operations.

    Redis Lists are perfect for message queues:
    - LPUSH adds to the left (producer)
    - BRPOP waits and removes from right (consumer)
    - Atomic operations, fast, simple
    """

    def __init__(self, redis_url: str):
        """Initialize Redis connection."""
        self.client = redis.from_url(redis_url, decode_responses=True)

    def push(self, queue_name: str, message: Dict[str, Any]) -> bool:
        """
        Push a message to the queue (producer).

        Args:
            queue_name: Name of the queue
            message: Dict to send (will be JSON serialized)

        Returns:
            True if successful
        """
        try:
            message_json = json.dumps(message)
            self.client.lpush(queue_name, message_json)
            return True
        except Exception as e:
            print(f"Error pushing message to Redis: {e}")
            return False

    def pop(self, queue_name: str, timeout: int = 0) -> Dict[str, Any] | None:
        """
        Pop a message from the queue (consumer).

        Args:
            queue_name: Name of the queue
            timeout: Seconds to wait (0 = wait forever)

        Returns:
            Message dict or None if timeout
        """
        try:
            result = self.client.brpop(queue_name, timeout=timeout)
            if result:
                _, message_json = result
                return json.loads(message_json)
            return None
        except Exception as e:
            print(f"Error popping message from Redis: {e}")
            return None

    def size(self, queue_name: str) -> int:
        """Get number of messages in queue."""
        return self.client.llen(queue_name)

    def close(self):
        """Close Redis connection."""
        self.client.close()
