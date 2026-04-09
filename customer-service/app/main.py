from fastapi import FastAPI
from app.database import engine, Base, settings
from app.routers import customers
from app.db_utils import wait_for_db

# Wait for database to be ready before creating tables
wait_for_db(settings.database_url)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Service", version="1.0.0", redirect_slashes=False)

app.include_router(customers.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}