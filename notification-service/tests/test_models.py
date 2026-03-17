import pytest
from datetime import datetime
from uuid import UUID, uuid4

from app.models.notification import Notification, NotificationStatus, NotificationType


@pytest.mark.unit
class TestNotificationModel:
    """Test cases for Notification model."""

    def test_create_notification_with_all_fields(self, db_session):
        """Test creating a notification with all fields."""
        customer_ids = [str(uuid4()), str(uuid4())]
        notification = Notification(
            notification_type=NotificationType.EMAIL,
            subject="Test Subject",
            body="Test Body",
            customer_ids=customer_ids,
            status=NotificationStatus.PENDING
        )
        db_session.add(notification)
        db_session.commit()

        assert isinstance(notification.id, UUID)
        assert notification.notification_type == NotificationType.EMAIL
        assert notification.subject == "Test Subject"
        assert notification.body == "Test Body"
        assert notification.customer_ids == customer_ids
        assert notification.status == NotificationStatus.PENDING
        assert isinstance(notification.created_at, datetime)
        assert isinstance(notification.updated_at, datetime)

    def test_notification_status_default(self, db_session):
        """Test that notification status defaults to PENDING."""
        notification = Notification(
            notification_type=NotificationType.EMAIL,
            subject="Test",
            body="Test",
            customer_ids=[str(uuid4())]
        )
        db_session.add(notification)
        db_session.commit()

        assert notification.status == NotificationStatus.PENDING

    def test_notification_status_transitions(self, db_session):
        """Test notification status state transitions."""
        notification = Notification(
            notification_type=NotificationType.EMAIL,
            subject="Test",
            body="Test",
            customer_ids=[str(uuid4())],
            status=NotificationStatus.PENDING
        )
        db_session.add(notification)
        db_session.commit()

        # Transition to PROCESSING
        notification.status = NotificationStatus.PROCESSING
        db_session.commit()
        assert notification.status == NotificationStatus.PROCESSING

        # Transition to COMPLETED
        notification.status = NotificationStatus.COMPLETED
        db_session.commit()
        assert notification.status == NotificationStatus.COMPLETED

    def test_notification_can_fail(self, db_session):
        """Test that notification can transition to FAILED status."""
        notification = Notification(
            notification_type=NotificationType.EMAIL,
            subject="Test",
            body="Test",
            customer_ids=[str(uuid4())],
            status=NotificationStatus.PROCESSING
        )
        db_session.add(notification)
        db_session.commit()

        # Transition to FAILED
        notification.status = NotificationStatus.FAILED
        db_session.commit()
        assert notification.status == NotificationStatus.FAILED

    def test_notification_timestamps(self, db_session):
        """Test that timestamps are set correctly."""
        notification = Notification(
            notification_type=NotificationType.EMAIL,
            subject="Test",
            body="Test",
            customer_ids=[str(uuid4())]
        )
        db_session.add(notification)
        db_session.commit()

        created_at = notification.created_at
        updated_at = notification.updated_at

        # Update the notification
        notification.status = NotificationStatus.COMPLETED
        db_session.commit()
        db_session.refresh(notification)

        # Created timestamp should not change
        assert notification.created_at == created_at
        # Updated timestamp should change
        assert notification.updated_at >= updated_at

    def test_query_notifications_by_status(self, db_session):
        """Test querying notifications by status."""
        # Create notifications with different statuses
        notification1 = Notification(
            notification_type=NotificationType.EMAIL,
            subject="Test 1",
            body="Test",
            customer_ids=[str(uuid4())],
            status=NotificationStatus.PENDING
        )
        notification2 = Notification(
            notification_type=NotificationType.EMAIL,
            subject="Test 2",
            body="Test",
            customer_ids=[str(uuid4())],
            status=NotificationStatus.COMPLETED
        )
        db_session.add_all([notification1, notification2])
        db_session.commit()

        pending = db_session.query(Notification).filter(
            Notification.status == NotificationStatus.PENDING
        ).all()

        assert len(pending) == 1
        assert pending[0].id == notification1.id

    def test_notification_with_multiple_customers(self, db_session):
        """Test notification with multiple customer IDs."""
        customer_ids = [str(uuid4()) for _ in range(5)]
        notification = Notification(
            notification_type=NotificationType.EMAIL,
            subject="Test",
            body="Test",
            customer_ids=customer_ids
        )
        db_session.add(notification)
        db_session.commit()

        assert len(notification.customer_ids) == 5
        assert all(cid in notification.customer_ids for cid in customer_ids)
