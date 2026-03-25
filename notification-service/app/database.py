from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    app_host: str = "0.0.0.0"
    app_port: int = 8002
    redis_url: str = "redis://localhost:6379"
    redis_email_queue: str = "email:queue"
    redis_sms_queue: str = "sms:queue"

    class Config:
        env_file = ".env"


settings = Settings()

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()