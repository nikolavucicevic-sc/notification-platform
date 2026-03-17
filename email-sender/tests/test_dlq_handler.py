import pytest
import json
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.messaging.dlq_handler import process_dlq_message, MAX_RETRIES


@pytest.mark.messaging
class TestDLQHandler:
    """Test cases for dead-letter queue handler."""

    @pytest.mark.asyncio
    @patch("app.messaging.dlq_handler.send_email")
    @patch("app.messaging.dlq_handler.publish_status")
    async def test_dlq_retry_success_on_first_retry(self, mock_publish, mock_send_email, mock_rabbitmq_channel):
        """Test successful retry on first attempt."""
        # Setup message with retry_count = 0
        message_data = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": [str(uuid4())],
            "retry_count": 0
        }

        mock_message = AsyncMock()
        mock_message.body = json.dumps(message_data).encode()

        mock_send_email.return_value = {
            "success": True,
            "status_code": 200
        }

        # Setup queue declaration
        mock_queue = AsyncMock()
        mock_rabbitmq_channel.declare_queue = AsyncMock(return_value=mock_queue)

        # Execute
        await process_dlq_message(mock_message, mock_rabbitmq_channel)

        # Verify email was retried
        mock_send_email.assert_called_once()

        # Verify status was published
        mock_publish.assert_called_once()

        # Verify message was acknowledged
        mock_message.ack.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.messaging.dlq_handler.send_email")
    @patch("app.messaging.dlq_handler.publish_status")
    async def test_dlq_retry_failure_requeue(self, mock_publish, mock_send_email, mock_rabbitmq_channel):
        """Test that failed retry is requeued with incremented retry count."""
        # Setup message with retry_count = 1
        message_data = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": [str(uuid4())],
            "retry_count": 1
        }

        mock_message = AsyncMock()
        mock_message.body = json.dumps(message_data).encode()

        # Simulate send failure
        mock_send_email.side_effect = Exception("Send failed")

        # Setup queue declaration
        mock_queue = AsyncMock()
        mock_queue.name = "email.send"
        mock_rabbitmq_channel.declare_queue = AsyncMock(return_value=mock_queue)
        mock_rabbitmq_channel.default_exchange.publish = AsyncMock()

        # Execute
        await process_dlq_message(mock_message, mock_rabbitmq_channel)

        # Verify message was republished to main queue
        mock_rabbitmq_channel.default_exchange.publish.assert_called_once()

        # Verify retry count was incremented
        call_args = mock_rabbitmq_channel.default_exchange.publish.call_args
        published_message = call_args[0][0]
        published_body = json.loads(published_message.body.decode())
        assert published_body["retry_count"] == 2

        # Verify message was acknowledged (after republishing)
        mock_message.ack.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.messaging.dlq_handler.send_email")
    @patch("app.messaging.dlq_handler.publish_status")
    async def test_dlq_max_retries_exceeded(self, mock_publish, mock_send_email, mock_rabbitmq_channel):
        """Test that messages exceeding max retries are marked as permanently failed."""
        # Setup message with retry_count = MAX_RETRIES
        message_data = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": [str(uuid4())],
            "retry_count": MAX_RETRIES
        }

        mock_message = AsyncMock()
        mock_message.body = json.dumps(message_data).encode()

        # Execute
        await process_dlq_message(mock_message, mock_rabbitmq_channel)

        # Verify email was NOT attempted (max retries exceeded)
        mock_send_email.assert_not_called()

        # Verify FAILED status was published
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args[0]
        results = call_args[2]
        assert results[0]["success"] is False
        assert "Failed after" in results[0]["error"]

        # Verify message was acknowledged (permanently failed)
        mock_message.ack.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.messaging.dlq_handler.send_email")
    @patch("app.messaging.dlq_handler.publish_status")
    async def test_dlq_multiple_customers_retry(self, mock_publish, mock_send_email, mock_rabbitmq_channel):
        """Test retry with multiple customers."""
        # Setup message with multiple customers
        customer_ids = [str(uuid4()), str(uuid4())]
        message_data = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": customer_ids,
            "retry_count": 0
        }

        mock_message = AsyncMock()
        mock_message.body = json.dumps(message_data).encode()

        mock_send_email.return_value = {
            "success": True,
            "status_code": 200
        }

        # Setup queue declaration
        mock_queue = AsyncMock()
        mock_rabbitmq_channel.declare_queue = AsyncMock(return_value=mock_queue)

        # Execute
        await process_dlq_message(mock_message, mock_rabbitmq_channel)

        # Verify send_email was called for each customer
        assert mock_send_email.call_count == 2

        # Verify status was published
        mock_publish.assert_called_once()

        # Verify message was acknowledged
        mock_message.ack.assert_called_once()

    @pytest.mark.asyncio
    async def test_dlq_malformed_message(self, mock_rabbitmq_channel):
        """Test handling of malformed message in DLQ."""
        # Setup malformed message
        mock_message = AsyncMock()
        mock_message.body = b"not valid json"

        # Execute
        await process_dlq_message(mock_message, mock_rabbitmq_channel)

        # Verify message was rejected without requeue
        mock_message.reject.assert_called_once_with(requeue=False)

    @pytest.mark.asyncio
    @patch("app.messaging.dlq_handler.send_email")
    @patch("app.messaging.dlq_handler.publish_status")
    async def test_dlq_retry_count_progression(self, mock_publish, mock_send_email, mock_rabbitmq_channel):
        """Test that retry count progresses correctly through attempts."""
        for retry_count in range(MAX_RETRIES):
            message_data = {
                "notification_id": str(uuid4()),
                "subject": "Test",
                "body": "Test body",
                "customer_ids": [str(uuid4())],
                "retry_count": retry_count
            }

            mock_message = AsyncMock()
            mock_message.body = json.dumps(message_data).encode()

            # Simulate failure to trigger requeue
            mock_send_email.side_effect = Exception("Send failed")

            # Setup queue declaration
            mock_queue = AsyncMock()
            mock_queue.name = "email.send"
            mock_rabbitmq_channel.declare_queue = AsyncMock(return_value=mock_queue)
            mock_rabbitmq_channel.default_exchange.publish = AsyncMock()

            # Execute
            await process_dlq_message(mock_message, mock_rabbitmq_channel)

            # Verify retry count was incremented
            if retry_count < MAX_RETRIES:
                call_args = mock_rabbitmq_channel.default_exchange.publish.call_args
                if call_args:  # Message was republished
                    published_message = call_args[0][0]
                    published_body = json.loads(published_message.body.decode())
                    assert published_body["retry_count"] == retry_count + 1

            # Reset mocks for next iteration
            mock_send_email.reset_mock()
            mock_publish.reset_mock()
            mock_rabbitmq_channel.default_exchange.publish.reset_mock()