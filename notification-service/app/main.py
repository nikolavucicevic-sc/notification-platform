from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import engine, Base, settings
from app.routers import notifications
from app.db_utils import wait_for_db
from app.redis_utils import wait_for_redis

# Wait for database to be ready before creating tables
wait_for_db(settings.database_url)

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Wait for Redis to be ready
    wait_for_redis(settings.redis_url)
    print("Notification Service started")
    yield
    print("Notification Service stopped")


app = FastAPI(title="Notification Service", version="1.0.0", lifespan=lifespan)

app.include_router(notifications.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}