from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import engine, Base, settings
from app.routers import notifications
from app.messaging.consumer import start_status_consumer

Base.metadata.create_all(bind=engine)

rabbit_connection = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rabbit_connection
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