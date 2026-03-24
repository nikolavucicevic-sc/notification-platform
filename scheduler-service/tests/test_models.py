import pytest
import logging
from datetime import datetime, timedelta
from uuid import uuid4

from app.models.scheduled_notification import (
    ScheduledNotification,
    ScheduleType,
    RecurrenceType,
    JobStatus
)

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestScheduledNotificationModel:
    """Tests for ScheduledNotification model"""

    def test_create_one_time_schedule(self, db_session):
        """Test creating a one-time scheduled notification."""
        logger.info("Testing one-time schedule model creation")
        scheduled_time = datetime.now() + timedelta(hours=1)
        customer_ids = [str(uuid4()), str(uuid4())]

        schedule = ScheduledNotification(
            schedule_type=ScheduleType.ONCE,
            scheduled_time=scheduled_time,
            notification_type="EMAIL",
            subject="Test notification",
            body="Test body",
            customer_ids=customer_ids,
            status=JobStatus.SCHEDULED
        )

        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        logger.info(f"Created schedule model with ID: {schedule.id}")
        assert schedule.id is not None
        assert schedule.schedule_type == ScheduleType.ONCE
        assert schedule.scheduled_time == scheduled_time
        assert schedule.customer_ids == customer_ids
        assert schedule.is_active is True
        assert schedule.run_count == "0"
        logger.info("✓ One-time schedule model created successfully")

    def test_create_recurring_schedule(self, db_session):
        """Test creating a recurring scheduled notification."""
        scheduled_time = datetime.now() + timedelta(hours=1)
        end_date = datetime.now() + timedelta(days=30)

        schedule = ScheduledNotification(
            schedule_type=ScheduleType.RECURRING,
            scheduled_time=scheduled_time,
            recurrence_type=RecurrenceType.DAILY,
            recurrence_end_date=end_date,
            notification_type="EMAIL",
            subject="Daily reminder",
            body="This is a daily reminder",
            customer_ids=[str(uuid4())],
            status=JobStatus.SCHEDULED
        )

        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.schedule_type == ScheduleType.RECURRING
        assert schedule.recurrence_type == RecurrenceType.DAILY
        assert schedule.recurrence_end_date == end_date

    def test_schedule_timestamps(self, db_session):
        """Test that created_at and updated_at timestamps are set."""
        schedule = ScheduledNotification(
            schedule_type=ScheduleType.ONCE,
            scheduled_time=datetime.now() + timedelta(hours=1),
            notification_type="EMAIL",
            subject="Test",
            body="Test body",
            customer_ids=[str(uuid4())],
            status=JobStatus.SCHEDULED
        )

        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.created_at is not None
        assert schedule.updated_at is not None
        assert schedule.created_at <= schedule.updated_at

    def test_schedule_default_values(self, db_session):
        """Test that default values are set correctly."""
        schedule = ScheduledNotification(
            schedule_type=ScheduleType.ONCE,
            scheduled_time=datetime.now() + timedelta(hours=1),
            notification_type="EMAIL",
            subject="Test",
            body="Test body",
            customer_ids=[str(uuid4())],
            status=JobStatus.SCHEDULED
        )

        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.is_active is True
        assert schedule.run_count == "0"
        assert schedule.last_run is None
        assert schedule.next_run is None

    def test_update_schedule(self, db_session):
        """Test updating a scheduled notification."""
        schedule = ScheduledNotification(
            schedule_type=ScheduleType.ONCE,
            scheduled_time=datetime.now() + timedelta(hours=1),
            notification_type="EMAIL",
            subject="Original subject",
            body="Original body",
            customer_ids=[str(uuid4())],
            status=JobStatus.SCHEDULED
        )

        db_session.add(schedule)
        db_session.commit()
        original_updated_at = schedule.updated_at

        # Update the schedule
        schedule.subject = "Updated subject"
        schedule.body = "Updated body"
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.subject == "Updated subject"
        assert schedule.body == "Updated body"
        assert schedule.updated_at >= original_updated_at

    def test_schedule_status_changes(self, db_session):
        """Test changing schedule status."""
        schedule = ScheduledNotification(
            schedule_type=ScheduleType.ONCE,
            scheduled_time=datetime.now() + timedelta(hours=1),
            notification_type="EMAIL",
            subject="Test",
            body="Test body",
            customer_ids=[str(uuid4())],
            status=JobStatus.SCHEDULED
        )

        db_session.add(schedule)
        db_session.commit()

        # Change to RUNNING
        schedule.status = JobStatus.RUNNING
        db_session.commit()
        assert schedule.status == JobStatus.RUNNING

        # Change to COMPLETED
        schedule.status = JobStatus.COMPLETED
        schedule.last_run = datetime.now()
        schedule.run_count = str(int(schedule.run_count) + 1)
        db_session.commit()

        assert schedule.status == JobStatus.COMPLETED
        assert schedule.last_run is not None
        assert schedule.run_count == "1"

    def test_pause_and_resume_schedule(self, db_session):
        """Test pausing and resuming a schedule."""
        schedule = ScheduledNotification(
            schedule_type=ScheduleType.RECURRING,
            scheduled_time=datetime.now() + timedelta(hours=1),
            recurrence_type=RecurrenceType.DAILY,
            notification_type="EMAIL",
            subject="Test",
            body="Test body",
            customer_ids=[str(uuid4())],
            status=JobStatus.SCHEDULED
        )

        db_session.add(schedule)
        db_session.commit()

        # Pause
        schedule.is_active = False
        db_session.commit()
        assert schedule.is_active is False

        # Resume
        schedule.is_active = True
        db_session.commit()
        assert schedule.is_active is True

    def test_cancel_schedule(self, db_session):
        """Test canceling a schedule."""
        schedule = ScheduledNotification(
            schedule_type=ScheduleType.ONCE,
            scheduled_time=datetime.now() + timedelta(hours=1),
            notification_type="EMAIL",
            subject="Test",
            body="Test body",
            customer_ids=[str(uuid4())],
            status=JobStatus.SCHEDULED
        )

        db_session.add(schedule)
        db_session.commit()

        # Cancel
        schedule.status = JobStatus.CANCELLED
        schedule.is_active = False
        db_session.commit()

        assert schedule.status == JobStatus.CANCELLED
        assert schedule.is_active is False

    def test_query_active_schedules(self, db_session):
        """Test querying only active schedules."""
        # Create active schedule
        active_schedule = ScheduledNotification(
            schedule_type=ScheduleType.ONCE,
            scheduled_time=datetime.now() + timedelta(hours=1),
            notification_type="EMAIL",
            subject="Active",
            body="Active schedule",
            customer_ids=[str(uuid4())],
            status=JobStatus.SCHEDULED,
            is_active=True
        )

        # Create inactive schedule
        inactive_schedule = ScheduledNotification(
            schedule_type=ScheduleType.ONCE,
            scheduled_time=datetime.now() + timedelta(hours=2),
            notification_type="EMAIL",
            subject="Inactive",
            body="Inactive schedule",
            customer_ids=[str(uuid4())],
            status=JobStatus.CANCELLED,
            is_active=False
        )

        db_session.add(active_schedule)
        db_session.add(inactive_schedule)
        db_session.commit()

        # Query only active
        active_schedules = db_session.query(ScheduledNotification).filter(
            ScheduledNotification.is_active == True
        ).all()

        assert len(active_schedules) == 1
        assert active_schedules[0].subject == "Active"

    def test_query_schedules_by_status(self, db_session):
        """Test querying schedules by status."""
        # Create schedules with different statuses
        scheduled = ScheduledNotification(
            schedule_type=ScheduleType.ONCE,
            scheduled_time=datetime.now() + timedelta(hours=1),
            notification_type="EMAIL",
            subject="Scheduled",
            body="Test",
            customer_ids=[str(uuid4())],
            status=JobStatus.SCHEDULED
        )

        completed = ScheduledNotification(
            schedule_type=ScheduleType.ONCE,
            scheduled_time=datetime.now() - timedelta(hours=1),
            notification_type="EMAIL",
            subject="Completed",
            body="Test",
            customer_ids=[str(uuid4())],
            status=JobStatus.COMPLETED
        )

        db_session.add(scheduled)
        db_session.add(completed)
        db_session.commit()

        # Query by status
        scheduled_items = db_session.query(ScheduledNotification).filter(
            ScheduledNotification.status == JobStatus.SCHEDULED
        ).all()

        assert len(scheduled_items) == 1
        assert scheduled_items[0].subject == "Scheduled"

    def test_multiple_customer_ids(self, db_session):
        """Test storing multiple customer IDs."""
        customer_ids = [str(uuid4()) for _ in range(5)]

        schedule = ScheduledNotification(
            schedule_type=ScheduleType.ONCE,
            scheduled_time=datetime.now() + timedelta(hours=1),
            notification_type="EMAIL",
            subject="Test",
            body="Test body",
            customer_ids=customer_ids,
            status=JobStatus.SCHEDULED
        )

        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        assert len(schedule.customer_ids) == 5
        assert schedule.customer_ids == customer_ids
