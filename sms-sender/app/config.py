from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    redis_sms_queue: str = "sms:queue"
    customer_service_url: str = "http://localhost:8001"
    sms_api_url: str = "http://localhost:8089/sms/send"

    class Config:
        env_file = ".env"


settings = Settings()
