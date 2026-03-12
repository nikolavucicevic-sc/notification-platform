from fastapi import FastAPI
from app.database import engine, Base, settings
from app.routers import customers

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Service", version="1.0.0")

app.include_router(customers.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}