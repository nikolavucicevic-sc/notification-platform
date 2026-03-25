from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    redis_sms_queue: str = "sms:queue"
    redis_dlq_queue: str = "sms:dlq"  # Dead Letter Queue
    customer_service_url: str = "http://localhost:8001"
    sms_api_url: str = "http://localhost:8089/sms/send"

    # Retry configuration
    max_retry_attempts: int = 3
    retry_backoff_base: int = 5  # Base seconds for exponential backoff

    class Config:
        env_file = ".env"


settings = Settings()
