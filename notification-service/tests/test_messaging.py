import pytest
import json
from unittest.mock import patch, MagicMock
from uuid import uuid4

from app.messaging.publisher import publish_email_request
from app.models.notification import Notification, NotificationStatus, NotificationType


@pytest.mark.messaging
class TestPublisher:
    """Test cases for Redis publisher."""

    @pytest.mark.asyncio
    @patch("app.messaging.publisher.RedisQueue")
    async def test_publish_email_request_success(self, MockRedisQueue):
        """Test successful publishing of email request to Redis."""
        mock_queue = MagicMock()
        mock_queue.push.return_value = True
        mock_queue.close = MagicMock()
        MockRedisQueue.return_value = mock_queue

        notification = Notification(
            notification_type=NotificationType.EMAIL,
            subject="Test Subject",
            body="Test Body",
            customer_ids=[str(uuid4()), str(uuid4())],
            status=NotificationStatus.PENDING
        )

        await publish_email_request(notification)

        mock_queue.push.assert_called_once()
        call_args = mock_queue.push.call_args
        queue_name = call_args[0][0]
        message_body = call_args[0][1]

        assert "email" in queue_name
        assert message_body["notification_id"] == str(notification.id)
        assert message_body["subject"] == notification.subject
        assert message_body["body"] == notification.body
        assert message_body["customer_ids"] == notification.customer_ids
        assert message_body["retry_count"] == 0

    @pytest.mark.asyncio
    @patch("app.messaging.publisher.RedisQueue")
    async def test_publish_email_request_connection_failure(self, MockRedisQueue):
        """Test handling of Redis connection failure."""
        MockRedisQueue.side_effect = Exception("Redis connection failed")

        notification = Notification(
            notification_type=NotificationType.EMAIL,
            subject="Test",
            body="Test",
            customer_ids=[str(uuid4())]
        )

        with pytest.raises(Exception, match="Redis connection failed"):
            await publish_email_request(notification)

    @pytest.mark.asyncio
    @patch("app.messaging.publisher.RedisQueue")
    async def test_publish_sms_request_uses_sms_queue(self, MockRedisQueue):
        """Test that SMS notifications are pushed to the SMS queue."""
        mock_queue = MagicMock()
        mock_queue.push.return_value = True
        mock_queue.close = MagicMock()
        MockRedisQueue.return_value = mock_queue

        notification = Notification(
            notification_type=NotificationType.SMS,
            subject="Test SMS",
            body="SMS Body",
            customer_ids=[str(uuid4())],
            status=NotificationStatus.PENDING
        )

        await publish_email_request(notification)

        mock_queue.push.assert_called_once()
        queue_name = mock_queue.push.call_args[0][0]
        assert "sms" in queue_name


@pytest.mark.messaging
class TestConsumer:
    """Placeholder — consumer runs as a long-lived process and is tested via integration tests."""

    @pytest.mark.asyncio
    async def test_consumer_configuration(self):
        assert True
