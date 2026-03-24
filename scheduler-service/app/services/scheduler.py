"""
Scheduler service using APScheduler to execute scheduled notifications.
"""
import asyncio
import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import settings, SessionLocal
from app.models.scheduled_notification import ScheduledNotification, JobStatus, RecurrenceType


# Global scheduler instance
scheduler = BackgroundScheduler()


def get_recurrence_trigger(recurrence_type: str, start_time: datetime):
    """Convert recurrence type to APScheduler CronTrigger"""
    if recurrence_type == RecurrenceType.HOURLY.value:
        return CronTrigger(minute=start_time.minute, second=start_time.second)
    elif recurrence_type == RecurrenceType.DAILY.value:
        return CronTrigger(hour=start_time.hour, minute=start_time.minute, second=start_time.second)
    elif recurrence_type == RecurrenceType.WEEKLY.value:
        return CronTrigger(day_of_week=start_time.weekday(), hour=start_time.hour, minute=start_time.minute)
    elif recurrence_type == RecurrenceType.MONTHLY.value:
        return CronTrigger(day=start_time.day, hour=start_time.hour, minute=start_time.minute)
    else:
        raise ValueError(f"Unknown recurrence type: {recurrence_type}")


async def execute_scheduled_notification(schedule_id: UUID):
    """
    Execute a scheduled notification by calling the notification service API.
    """
    db = SessionLocal()
    try:
        # Get the scheduled notification
        scheduled_notif = db.query(ScheduledNotification).filter(
            ScheduledNotification.id == schedule_id
        ).first()

        if not scheduled_notif or not scheduled_notif.is_active:
            print(f"Scheduled notification {schedule_id} not found or inactive")
            return

        # Update status to RUNNING
        scheduled_notif.status = JobStatus.RUNNING
        db.commit()

        # Prepare notification payload
        notification_payload = {
            "notification_type": scheduled_notif.notification_type,
            "subject": scheduled_notif.subject,
            "body": scheduled_notif.body,
            "customer_ids": scheduled_notif.customer_ids
        }

        # Call notification service API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.notification_service_url}/notifications/",
                json=notification_payload
            )
            response.raise_for_status()

        # Update status and tracking
        scheduled_notif.status = JobStatus.COMPLETED
        scheduled_notif.last_run = datetime.now()
        scheduled_notif.run_count = str(int(scheduled_notif.run_count) + 1)

        # For one-time jobs, mark as inactive
        if scheduled_notif.schedule_type.value == "ONCE":
            scheduled_notif.is_active = False

        # Check if recurring job should end
        if scheduled_notif.recurrence_end_date and datetime.now() >= scheduled_notif.recurrence_end_date:
            scheduled_notif.is_active = False
            if scheduled_notif.job_id:
                scheduler.remove_job(scheduled_notif.job_id)

        db.commit()
        print(f"✓ Successfully executed scheduled notification {schedule_id}")

    except Exception as e:
        print(f"✗ Failed to execute scheduled notification {schedule_id}: {e}")
        if scheduled_notif:
            scheduled_notif.status = JobStatus.FAILED
            db.commit()
    finally:
        db.close()


def _execute_scheduled_notification_sync(schedule_id: UUID):
    """Wrapper to run async function in sync context"""
    asyncio.run(execute_scheduled_notification(schedule_id))


def add_job_to_scheduler(scheduled_notif: ScheduledNotification, db: Session):
    """Add a job to APScheduler based on scheduled notification details"""
    if scheduled_notif.schedule_type.value == "ONCE":
        # One-time job
        trigger = DateTrigger(run_date=scheduled_notif.scheduled_time)
    else:
        # Recurring job
        trigger = get_recurrence_trigger(
            scheduled_notif.recurrence_type.value,
            scheduled_notif.scheduled_time
        )

    # Add job to scheduler
    job = scheduler.add_job(
        func=lambda: _execute_scheduled_notification_sync(scheduled_notif.id),
        trigger=trigger,
        id=str(scheduled_notif.id),
        name=f"Schedule: {scheduled_notif.subject}",
        replace_existing=True
    )

    # Update database with job ID and next run time
    scheduled_notif.job_id = job.id
    scheduled_notif.next_run = job.next_run_time
    db.commit()

    print(f"✓ Added job {job.id} to scheduler, next run: {job.next_run_time}")


def remove_job_from_scheduler(job_id: str):
    """Remove a job from APScheduler"""
    try:
        scheduler.remove_job(job_id)
        print(f"✓ Removed job {job_id} from scheduler")
    except Exception as e:
        print(f"⚠️  Failed to remove job {job_id}: {e}")


def start_scheduler():
    """Start the APScheduler"""
    if not scheduler.running:
        scheduler.start()
        print("✓ Scheduler started")


def stop_scheduler():
    """Stop the APScheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("✓ Scheduler stopped")


def load_existing_jobs():
    """Load all active scheduled notifications from database into scheduler"""
    db = SessionLocal()
    try:
        scheduled_notifs = db.query(ScheduledNotification).filter(
            ScheduledNotification.is_active == True,
            ScheduledNotification.status != JobStatus.CANCELLED
        ).all()

        for notif in scheduled_notifs:
            try:
                add_job_to_scheduler(notif, db)
            except Exception as e:
                print(f"⚠️  Failed to load job {notif.id}: {e}")

        print(f"✓ Loaded {len(scheduled_notifs)} existing jobs")
    finally:
        db.close()
