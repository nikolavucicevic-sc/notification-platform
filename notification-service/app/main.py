from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import engine, Base, settings
from app.routers import notifications
from app.messaging.consumer import start_status_consumer
from app.db_utils import wait_for_db

# Wait for database to be ready before creating tables
wait_for_db(settings.database_url)

Base.metadata.create_all(bind=engine)

rabbit_connection = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rabbit_connection
    # Import here to avoid circular imports
    from app.rabbitmq_utils import wait_for_rabbitmq

    # Wait for RabbitMQ to be ready
    await wait_for_rabbitmq(settings.rabbitmq_url)

    rabbit_connection = await start_status_consumer()
    print("Notification Service started")
    yield
    if rabbit_connection:
        await rabbit_connection.close()
    print("Notification Service stopped")


app = FastAPI(title="Notification Service", version="1.0.0", lifespan=lifespan)

app.include_router(notifications.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}