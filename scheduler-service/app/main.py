from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import engine, Base, settings
from app.routers import scheduled_notifications
from app.services.scheduler import start_scheduler, stop_scheduler, load_existing_jobs
from app.db_utils import wait_for_db

# Wait for database to be ready before creating tables
wait_for_db(settings.database_url)

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start scheduler and load existing jobs
    start_scheduler()
    load_existing_jobs()
    print("Scheduler Service started")
    yield
    # Shutdown: Stop scheduler
    stop_scheduler()
    print("Scheduler Service stopped")


app = FastAPI(
    title="Scheduler Service",
    version="1.0.0",
    description="Service for scheduling notifications",
    lifespan=lifespan,
    redirect_slashes=False,
    openapi_url="/api/schedules/openapi.json",
)

app.include_router(scheduled_notifications.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "service": "Scheduler Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "schedules": "/schedules",
            "docs": "/docs"
        }
    }
