from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis

from app.database import get_db, settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint that verifies:
    - API is responding
    - Database connection is working
    - Redis connection is working
    - Queue depths
    """
    health_status = {
        "status": "healthy",
        "service": "notification-service",
        "checks": {}
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "PostgreSQL connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database error: {str(e)}"
        }

    # Check Redis
    try:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        redis_client.ping()

        # Get queue depths
        email_queue_depth = redis_client.llen(settings.redis_email_queue)
        sms_queue_depth = redis_client.llen(settings.redis_sms_queue)

        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful",
            "queues": {
                "email_queue": email_queue_depth,
                "sms_queue": sms_queue_depth
            }
        }
        redis_client.close()
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis error: {str(e)}"
        }

    return health_status


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness probe for Kubernetes/Docker health checks.
    Returns 200 if service is ready to accept traffic.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}


@router.get("/live")
async def liveness_check():
    """
    Liveness probe for Kubernetes/Docker health checks.
    Returns 200 if service is alive (even if not fully ready).
    """
    return {"status": "alive"}
