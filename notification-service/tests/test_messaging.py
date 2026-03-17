import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.messaging.publisher import publish_email_request
from app.models.notification import Notification, NotificationStatus, NotificationType


@pytest.mark.messaging
class TestPublisher:
    """Test cases for RabbitMQ publisher."""

    @pytest.mark.asyncio
    @patch("app.messaging.publisher.aio_pika.connect_robust")
    async def test_publish_email_request_success(self, mock_connect):
        """Test successful publishing of email request."""
        # Setup mocks
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_queue = AsyncMock()
        mock_queue.name = "email.send"

        mock_channel.declare_exchange = AsyncMock()
        mock_channel.declare_queue = AsyncMock(return_value=mock_queue)
        mock_channel.default_exchange.publish = AsyncMock()

        mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
        mock_connection.__aexit__ = AsyncMock(return_value=None)
        mock_connection.channel = AsyncMock(return_value=mock_channel)

        mock_connect.return_value = mock_connection

        # Create a test notification
        notification = Notification(
            notification_type=NotificationType.EMAIL,
            subject="Test Subject",
            body="Test Body",
            customer_ids=[str(uuid4()), str(uuid4())],
            status=NotificationStatus.PENDING
        )

        # Execute
        await publish_email_request(notification)

        # Verify connection was established
        mock_connect.assert_called_once()

        # Verify channel was created
        mock_connection.channel.assert_called_once()

        # Verify DLX and DLQ were declared
        assert mock_channel.declare_exchange.call_count == 1
        assert mock_channel.declare_queue.call_count == 2

        # Verify message was published
        mock_channel.default_exchange.publish.assert_called_once()

        # Verify message content
        call_args = mock_channel.default_exchange.publish.call_args
        message = call_args[0][0]
        routing_key = call_args[1]["routing_key"]

        assert routing_key == "email.send"

        # Parse message body
        message_body = json.loads(message.body.decode())
        assert message_body["notification_id"] == str(notification.id)
        assert message_body["subject"] == notification.subject
        assert message_body["body"] == notification.body
        assert message_body["customer_ids"] == notification.customer_ids
        assert message_body["retry_count"] == 0

    @pytest.mark.asyncio
    @patch("app.messaging.publisher.aio_pika.connect_robust")
    async def test_publish_email_request_connection_failure(self, mock_connect):
        """Test handling of connection failure."""
        mock_connect.side_effect = Exception("Connection failed")

        notification = Notification(
            notification_type=NotificationType.EMAIL,
            subject="Test",
            body="Test",
            customer_ids=[str(uuid4())]
        )

        with pytest.raises(Exception, match="Connection failed"):
            await publish_email_request(notification)


@pytest.mark.messaging
class TestConsumer:
    """Test cases for RabbitMQ consumer (status updates)."""

    @pytest.mark.asyncio
    async def test_consumer_configuration(self):
        """Test that consumer is properly configured."""
        # This is a placeholder test - actual consumer tests would require
        # running the consumer service and simulating message delivery
        # In a real scenario, you'd test:
        # 1. Consumer connects to the correct queue
        # 2. Consumer processes status updates correctly
        # 3. Consumer updates notification status in database
        # 4. Consumer acknowledges messages properly
        assert True  # Placeholder
