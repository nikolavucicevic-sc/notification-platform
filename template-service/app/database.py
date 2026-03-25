from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.template import Base
from contextlib import contextmanager
import os
import time

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@postgres:5432/notification_platform")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def wait_for_db(max_retries=30, delay=1):
    """Wait for database to become available"""
    for attempt in range(1, max_retries + 1):
        try:
            print("Waiting for database to become available...")
            engine.connect()
            print(f"✓ Database connection established on attempt {attempt}")
            return
        except Exception as e:
            if attempt == max_retries:
                print(f"✗ Failed to connect to database after {max_retries} attempts")
                raise
            print(f"  Attempt {attempt}/{max_retries} failed: {e}")
            time.sleep(delay)


def init_db():
    """Initialize database tables"""
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database session"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
