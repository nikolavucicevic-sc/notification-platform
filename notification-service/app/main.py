from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base, settings
from app.routers import notifications, health, dlq
from app.db_utils import wait_for_db
from app.redis_utils import wait_for_redis

# Wait for database to be ready before creating tables
wait_for_db(settings.database_url)

Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Wait for Redis to be ready
    wait_for_redis(settings.redis_url)
    print("Notification Service started")
    yield
    print("Notification Service stopped")


app = FastAPI(title="Notification Service", version="1.0.0", lifespan=lifespan)

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

app.include_router(notifications.router)
app.include_router(health.router)
app.include_router(dlq.router)