from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
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

# Wait for database to be ready before creating tables
wait_for_db(settings.database_url)

Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Wait for Redis to be ready
    wait_for_redis(settings.redis_url)
    print("✅ Notification Service started")
    print("📊 Prometheus metrics available at /metrics")
    print("🔐 Authentication enabled - JWT and API keys supported")
    yield
    print("Notification Service stopped")


app = FastAPI(
    title="Notification Platform API",
    version="2.0.0",
    description="Enterprise notification platform with authentication, monitoring, and distributed tracing",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint for monitoring."""
    return metrics_endpoint()