from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    redis_email_queue: str = "email:queue"
    redis_dlq_queue: str = "email:dlq"  # Dead Letter Queue
    wiremock_url: str = "http://localhost:8089"

    # Retry configuration
    max_retry_attempts: int = 3
    retry_backoff_base: int = 5  # Base seconds for exponential backoff

    class Config:
        env_file = ".env"


settings = Settings()
