import pytest
import json
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.messaging.consumer import process_email_request


@pytest.mark.messaging
class TestEmailConsumer:
    """Test cases for email consumer."""

    @pytest.mark.asyncio
    @patch("app.messaging.consumer.send_email")
    @patch("app.messaging.consumer.publish_status")
    async def test_process_email_request_success(self, mock_publish, mock_send_email, mock_rabbitmq_message, mock_rabbitmq_channel):
        """Test successful email request processing."""
        # Setup
        mock_send_email.return_value = {
            "customer_id": "customer-123",
            "success": True,
            "status_code": 200
        }

        # Execute
        await process_email_request(mock_rabbitmq_message, mock_rabbitmq_channel)

        # Verify email was sent
        mock_send_email.assert_called_once()

        # Verify status was published
        mock_publish.assert_called_once()

        # Verify message was acknowledged
        mock_rabbitmq_message.ack.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.messaging.consumer.send_email")
    @patch("app.messaging.consumer.publish_status")
    async def test_process_email_request_multiple_customers(self, mock_publish, mock_send_email, mock_rabbitmq_channel):
        """Test processing email request with multiple customers."""
        # Setup message with multiple customers
        customer_ids = [str(uuid4()), str(uuid4()), str(uuid4())]
        message_data = {
            "notification_id": str(uuid4()),
            "subject": "Test",
            "body": "Test body",
            "customer_ids": customer_ids,
            "retry_count": 0
        }

        mock_message = AsyncMock()
        mock_message.body = json.dumps(message_data).encode()
        mock_message.delivery_tag = 1

        mock_send_email.return_value = {
            "success": True,
            "status_code": 200
        }

        # Execute
        await process_email_request(mock_message, mock_rabbitmq_channel)

        # Verify send_email was called for each customer
        assert mock_send_email.call_count == 3

        # Verify status was published
        mock_publish.assert_called_once()

        # Verify message was acknowledged
        mock_message.ack.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.messaging.consumer.send_email")
    @patch("app.messaging.consumer.publish_status")
    async def test_process_email_request_send_failure(self, mock_publish, mock_send_email, mock_rabbitmq_message, mock_rabbitmq_channel):
        """Test handling of email sending failure."""
        # Setup
        mock_send_email.side_effect = Exception("Email service unavailable")

        # Execute
        await process_email_request(mock_rabbitmq_message, mock_rabbitmq_channel)

        # Verify message was rejected (will go to DLQ)
        mock_rabbitmq_message.reject.assert_called_once_with(requeue=False)

        # Verify FAILED status was published
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args[0]
        results = call_args[2]
        assert results[0]["success"] is False

    @pytest.mark.asyncio
    async def test_process_email_request_malformed_message(self, mock_rabbitmq_channel):
        """Test handling of malformed message."""
        # Setup malformed message
        mock_message = AsyncMock()
        mock_message.body = b"not valid json"
        mock_message.delivery_tag = 1

        # Execute
        await process_email_request(mock_message, mock_rabbitmq_channel)

        # Verify message was rejected without requeue
        mock_message.reject.assert_called_once_with(requeue=False)

    @pytest.mark.asyncio
    @patch("app.messaging.consumer.send_email")
    @patch("app.messaging.consumer.publish_status")
    async def test_process_email_request_partial_success(self, mock_publish, mock_send_email, mock_rabbitmq_channel):
        """Test processing where some emails succeed and some fail."""
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

        # First call succeeds, second fails
        mock_send_email.side_effect = [
            {"customer_id": customer_ids[0], "success": True, "status_code": 200},
            {"customer_id": customer_ids[1], "success": False, "status_code": 500}
        ]

        # Execute
        await process_email_request(mock_message, mock_rabbitmq_channel)

        # Verify both emails were attempted
        assert mock_send_email.call_count == 2

        # Verify status was published with both results
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args[0]
        results = call_args[2]
        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[1]["success"] is False

        # Message should still be acknowledged (partial success scenario)
        mock_message.ack.assert_called_once()