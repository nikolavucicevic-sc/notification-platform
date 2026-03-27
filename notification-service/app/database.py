from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.pool import Pool
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    database_url: str
    app_host: str = "0.0.0.0"
    app_port: int = 8002
    redis_url: str = "redis://localhost:6379"
    redis_email_queue: str = "email:queue"
    redis_sms_queue: str = "sms:queue"

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Database connection pool settings
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    json_logs: bool = os.getenv("JSON_LOGS", "true").lower() == "true"

    class Config:
        env_file = ".env"


settings = Settings()

# Create engine with optimized connection pooling (only for PostgreSQL)
# SQLite doesn't support pooling, so we only add pool arguments for PostgreSQL
if settings.database_url.startswith("sqlite"):
    # SQLite: Simple engine for testing
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}  # Allow SQLite in multi-threaded tests
    )
else:
    # PostgreSQL: Production engine with connection pooling
    engine = create_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,         # Number of persistent connections
        max_overflow=settings.db_max_overflow,   # Additional connections when pool is full
        pool_timeout=settings.db_pool_timeout,   # Seconds to wait for available connection
        pool_recycle=settings.db_pool_recycle,   # Recycle connections after 1 hour
        pool_pre_ping=True,                       # Verify connection health before use
        echo_pool=settings.environment == "development",  # Log pool events in dev
    )


# Add connection pool listeners for monitoring
@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log when new database connection is created."""
    # In production, this would use structlog
    pass


@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when connection is checked out from pool."""
    # In production, this would use structlog
    pass


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()