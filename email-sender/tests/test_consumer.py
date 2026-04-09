import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.messaging.consumer import process_email_request


@pytest.mark.messaging
class TestEmailConsumer:
    """Test cases for email consumer (Redis-based)."""

    @pytest.mark.asyncio
    @patch("app.messaging.consumer.send_email")
    @patch("app.messaging.consumer.update_notification_status")
    async def test_process_email_request_success(self, mock_update_status, mock_send_email):
        """Test successful email request processing."""
        customer_id = str(uuid4())
        message = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": [customer_id],
            "retry_count": 0
        }
        mock_redis_queue = MagicMock()
        mock_send_email.return_value = {"success": True, "status_code": 201}

        await process_email_request(message, mock_redis_queue)

        mock_send_email.assert_called_once()
        mock_update_status.assert_called_once_with(message["notification_id"], "COMPLETED")

    @pytest.mark.asyncio
    @patch("app.messaging.consumer.send_email")
    @patch("app.messaging.consumer.update_notification_status")
    async def test_process_email_request_multiple_customers(self, mock_update_status, mock_send_email):
        """Test processing email request with multiple customers."""
        customer_ids = [str(uuid4()), str(uuid4()), str(uuid4())]
        message = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": customer_ids,
            "retry_count": 0
        }
        mock_redis_queue = MagicMock()
        mock_send_email.return_value = {"success": True, "status_code": 201}

        await process_email_request(message, mock_redis_queue)

        assert mock_send_email.call_count == 3
        mock_update_status.assert_called_once_with(message["notification_id"], "COMPLETED")

    @pytest.mark.asyncio
    @patch("app.messaging.consumer.send_email")
    @patch("app.messaging.consumer.update_notification_status")
    async def test_process_email_request_send_failure_retries(self, mock_update_status, mock_send_email):
        """Test that a failed send is retried by pushing back to the queue."""
        message = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": [str(uuid4())],
            "retry_count": 0
        }
        mock_redis_queue = MagicMock()
        mock_send_email.side_effect = Exception("Email service unavailable")

        await process_email_request(message, mock_redis_queue)

        # Should push back to the email queue for retry (not DLQ yet)
        mock_redis_queue.push.assert_called_once()
        pushed_queue = mock_redis_queue.push.call_args[0][0]
        pushed_message = mock_redis_queue.push.call_args[0][1]
        assert "email" in pushed_queue
        assert pushed_message["retry_count"] == 1

    @pytest.mark.asyncio
    @patch("app.messaging.consumer.send_email")
    @patch("app.messaging.consumer.update_notification_status")
    async def test_process_email_request_max_retries_goes_to_dlq(self, mock_update_status, mock_send_email):
        """Test that a message at max retries is pushed to DLQ and marked FAILED."""
        from app.config import settings
        message = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": [str(uuid4())],
            "retry_count": settings.max_retry_attempts  # already at max
        }
        mock_redis_queue = MagicMock()
        mock_send_email.side_effect = Exception("Still failing")

        await process_email_request(message, mock_redis_queue)

        mock_redis_queue.push.assert_called_once()
        pushed_queue = mock_redis_queue.push.call_args[0][0]
        assert "dlq" in pushed_queue
        mock_update_status.assert_called_once_with(message["notification_id"], "FAILED")
