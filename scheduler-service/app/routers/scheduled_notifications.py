from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.database import get_db
from app.models.scheduled_notification import ScheduledNotification, JobStatus, ScheduleType
from app.schemas.scheduled_notification import (
    ScheduledNotificationCreate,
    ScheduledNotificationUpdate,
    ScheduledNotificationResponse
)
from app.services.scheduler import add_job_to_scheduler, remove_job_from_scheduler

router = APIRouter(prefix="/schedules", tags=["schedules"], redirect_slashes=False)


@router.post("", response_model=ScheduledNotificationResponse, status_code=201)
def create_scheduled_notification(
    schedule: ScheduledNotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new scheduled notification"""
    # Validate recurrence settings
    if schedule.schedule_type == "RECURRING" and not schedule.recurrence_type:
        raise HTTPException(status_code=400, detail="recurrence_type is required for RECURRING schedules")

    # Create database record
    db_schedule = ScheduledNotification(
        schedule_type=ScheduleType[schedule.schedule_type],
        scheduled_time=schedule.scheduled_time,
        recurrence_type=schedule.recurrence_type,
        recurrence_end_date=schedule.recurrence_end_date,
        notification_type=schedule.notification_type,
        subject=schedule.subject,
        body=schedule.body,
        customer_ids=[str(cid) for cid in schedule.customer_ids],
        created_by=schedule.created_by,
        status=JobStatus.SCHEDULED
    )

    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)

    # Add to scheduler
    try:
        add_job_to_scheduler(db_schedule, db)
    except Exception as e:
        db_schedule.status = JobStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to schedule job: {str(e)}")

    return db_schedule


@router.get("", response_model=List[ScheduledNotificationResponse])
def get_scheduled_notifications(
    status: str = None,
    is_active: bool = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all scheduled notifications with optional filters"""
    query = db.query(ScheduledNotification)

    if status:
        query = query.filter(ScheduledNotification.status == JobStatus[status])
    if is_active is not None:
        query = query.filter(ScheduledNotification.is_active == is_active)

    return query.offset(skip).limit(limit).all()


@router.get("/{schedule_id}", response_model=ScheduledNotificationResponse)
def get_scheduled_notification(schedule_id: UUID, db: Session = Depends(get_db)):
    """Get a specific scheduled notification by ID"""
    schedule = db.query(ScheduledNotification).filter(
        ScheduledNotification.id == schedule_id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Scheduled notification not found")

    return schedule


@router.put("/{schedule_id}", response_model=ScheduledNotificationResponse)
def update_scheduled_notification(
    schedule_id: UUID,
    schedule_update: ScheduledNotificationUpdate,
    db: Session = Depends(get_db)
):
    """Update a scheduled notification"""
    schedule = db.query(ScheduledNotification).filter(
        ScheduledNotification.id == schedule_id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Scheduled notification not found")

    # Update fields
    update_data = schedule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "customer_ids" and value:
            setattr(schedule, field, [str(cid) for cid in value])
        else:
            setattr(schedule, field, value)

    db.commit()
    db.refresh(schedule)

    # Reschedule if active
    if schedule.is_active and schedule.job_id:
        try:
            remove_job_from_scheduler(schedule.job_id)
            add_job_to_scheduler(schedule, db)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to reschedule job: {str(e)}")

    return schedule


@router.delete("/{schedule_id}", status_code=204)
def cancel_scheduled_notification(schedule_id: UUID, db: Session = Depends(get_db)):
    """Cancel a scheduled notification"""
    schedule = db.query(ScheduledNotification).filter(
        ScheduledNotification.id == schedule_id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Scheduled notification not found")

    # Remove from scheduler
    if schedule.job_id:
        remove_job_from_scheduler(schedule.job_id)

    # Update status
    schedule.status = JobStatus.CANCELLED
    schedule.is_active = False
    db.commit()


@router.post("/{schedule_id}/pause", response_model=ScheduledNotificationResponse)
def pause_scheduled_notification(schedule_id: UUID, db: Session = Depends(get_db)):
    """Pause a scheduled notification"""
    schedule = db.query(ScheduledNotification).filter(
        ScheduledNotification.id == schedule_id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Scheduled notification not found")

    if schedule.job_id:
        remove_job_from_scheduler(schedule.job_id)

    schedule.is_active = False
    db.commit()
    db.refresh(schedule)

    return schedule


@router.post("/{schedule_id}/resume", response_model=ScheduledNotificationResponse)
def resume_scheduled_notification(schedule_id: UUID, db: Session = Depends(get_db)):
    """Resume a paused scheduled notification"""
    schedule = db.query(ScheduledNotification).filter(
        ScheduledNotification.id == schedule_id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Scheduled notification not found")

    schedule.is_active = True
    db.commit()

    try:
        add_job_to_scheduler(schedule, db)
    except Exception as e:
        schedule.is_active = False
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to resume job: {str(e)}")

    db.refresh(schedule)
    return schedule
