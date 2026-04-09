import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.messaging.dlq_handler import process_dlq_message, MAX_RETRIES


@pytest.mark.messaging
class TestDLQHandler:
    """Test cases for dead-letter queue handler (Redis-based)."""

    @pytest.mark.asyncio
    @patch("app.messaging.dlq_handler.send_email")
    @patch("app.messaging.dlq_handler.publish_status")
    async def test_dlq_retry_success_on_first_retry(self, mock_publish, mock_send_email):
        """Test successful retry on first attempt."""
        message = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": [str(uuid4())],
            "retry_count": 0
        }
        mock_redis_queue = MagicMock()
        mock_send_email.return_value = {"success": True, "status_code": 201}

        await process_dlq_message(message, mock_redis_queue)

        mock_send_email.assert_called_once()
        mock_publish.assert_called_once()
        mock_redis_queue.push.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.messaging.dlq_handler.send_email")
    @patch("app.messaging.dlq_handler.publish_status")
    async def test_dlq_retry_failure_requeue(self, mock_publish, mock_send_email):
        """Test that failed retry is requeued with incremented retry count."""
        message = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": [str(uuid4())],
            "retry_count": 1
        }
        mock_redis_queue = MagicMock()
        mock_send_email.side_effect = Exception("Send failed")

        await process_dlq_message(message, mock_redis_queue)

        mock_redis_queue.push.assert_called_once()
        pushed_message = mock_redis_queue.push.call_args[0][1]
        assert pushed_message["retry_count"] == 2

    @pytest.mark.asyncio
    @patch("app.messaging.dlq_handler.send_email")
    @patch("app.messaging.dlq_handler.publish_status")
    async def test_dlq_max_retries_exceeded(self, mock_publish, mock_send_email):
        """Test that messages exceeding max retries are marked as permanently failed."""
        message = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": [str(uuid4())],
            "retry_count": MAX_RETRIES
        }
        mock_redis_queue = MagicMock()

        await process_dlq_message(message, mock_redis_queue)

        mock_send_email.assert_not_called()
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args[0]
        results = call_args[1]
        assert results[0]["success"] is False
        assert "Failed after" in results[0]["error"]
        mock_redis_queue.push.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.messaging.dlq_handler.send_email")
    @patch("app.messaging.dlq_handler.publish_status")
    async def test_dlq_multiple_customers_retry(self, mock_publish, mock_send_email):
        """Test retry with multiple customers."""
        customer_ids = [str(uuid4()), str(uuid4())]
        message = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": customer_ids,
            "retry_count": 0
        }
        mock_redis_queue = MagicMock()
        mock_send_email.return_value = {"success": True, "status_code": 201}

        await process_dlq_message(message, mock_redis_queue)

        assert mock_send_email.call_count == 2
        mock_publish.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.messaging.dlq_handler.send_email")
    @patch("app.messaging.dlq_handler.publish_status")
    async def test_dlq_retry_count_progression(self, mock_publish, mock_send_email):
        """Test that retry count progresses correctly through attempts."""
        mock_redis_queue = MagicMock()
        mock_send_email.side_effect = Exception("Send failed")

        for retry_count in range(MAX_RETRIES):
            message = {
                "notification_id": str(uuid4()),
                "subject": "Test",
                "body": "Test body",
                "customer_ids": [str(uuid4())],
                "retry_count": retry_count
            }
            mock_redis_queue.reset_mock()

            await process_dlq_message(message, mock_redis_queue)

            mock_redis_queue.push.assert_called_once()
            pushed_message = mock_redis_queue.push.call_args[0][1]
            assert pushed_message["retry_count"] == retry_count + 1
