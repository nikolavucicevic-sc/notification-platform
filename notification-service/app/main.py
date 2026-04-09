from contextlib import asynccontextmanager
import signal
import asyncio
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base, settings
from app.routers import notifications, health, dlq, auth
from app.db_utils import wait_for_db
from app.redis_utils import wait_for_redis
from app.metrics import metrics_endpoint, MetricsMiddleware
from app.tracing import setup_tracing
from app.logging_config import configure_logging, get_logger
from app.middleware import RequestIDMiddleware, UserContextMiddleware

# Configure structured logging
configure_logging(
    log_level=settings.log_level,
    json_logs=settings.json_logs
)
logger = get_logger(__name__)

# Wait for database to be ready before creating tables
wait_for_db(settings.database_url)
# Schema migrations are handled by Alembic (runs via start.sh before this process starts)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Global shutdown event
shutdown_event = asyncio.Event()


def handle_shutdown_signal(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("shutdown_signal_received", signal=signum)
    shutdown_event.set()


# Register signal handlers
signal.signal(signal.SIGTERM, handle_shutdown_signal)
signal.signal(signal.SIGINT, handle_shutdown_signal)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    wait_for_redis(settings.redis_url)
    logger.info(
        "service_started",
        environment=settings.environment,
        port=settings.app_port,
        log_level=settings.log_level,
        pool_size=settings.db_pool_size
    )
    logger.info("metrics_available", endpoint="/metrics")
    logger.info("authentication_enabled", methods=["JWT", "API_KEY"])

    yield

    # Graceful shutdown
    logger.info("service_shutting_down")

    # Wait for in-flight requests to complete (max 30 seconds)
    try:
        await asyncio.wait_for(shutdown_event.wait(), timeout=30.0)
    except asyncio.TimeoutError:
        logger.warning("shutdown_timeout", message="Some requests may have been interrupted")

    # Dispose database connections
    logger.info("closing_database_connections")
    engine.dispose()

    logger.info("service_stopped")


app = FastAPI(
    title="Bemby Notify API",
    version="2.0.0",
    description="Bemby Notify — enterprise notification platform with authentication, monitoring, and distributed tracing",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add custom middleware (order matters!)
app.add_middleware(RequestIDMiddleware)  # Must be first for request tracing
app.add_middleware(UserContextMiddleware)  # Add user context to logs

# Add CORS middleware
cors_origins = ["*"] if settings.environment != "production" else [
    "http://18.156.176.60:3000",  # EC2 instance
    "http://18.156.176.60",       # EC2 instance without port
    "https://yourdomain.com",     # Replace with actual production domain when available
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# Set up distributed tracing with OpenTelemetry
try:
    setup_tracing(app, service_name="notification-service")
except Exception as e:
    print(f"⚠️  Warning: Could not set up tracing: {e}")
    print("   Continuing without distributed tracing...")

# Include routers
app.include_router(auth.router)
app.include_router(notifications.router)
app.include_router(health.router)
app.include_router(dlq.router)

# Global exception handler — catches unhandled exceptions, logs root cause, returns clean 500
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        method=request.method,
        path=request.url.path,
        error_type=type(exc).__name__,
        error=str(exc),
        traceback=traceback.format_exc()
    )
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {type(exc).__name__}"}
    )


# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint for monitoring."""
    return metrics_endpoint()