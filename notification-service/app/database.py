from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    app_host: str = "0.0.0.0"
    app_port: int = 8002
    rabbitmq_url: str
    rabbitmq_email_queue: str = "email.send"
    rabbitmq_status_queue: str = "email.status"

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