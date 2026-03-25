from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.routes import templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler"""
    # Startup
    init_db()
    print("Template Service started")
    yield
    # Shutdown
    print("Template Service stopped")


app = FastAPI(
    title="Template Service",
    description="Service for managing notification templates with variable substitution",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(templates.router, prefix="/templates", tags=["templates"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "template-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
