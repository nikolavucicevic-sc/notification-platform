from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    redis_email_queue: str = "email:queue"
    wiremock_url: str = "http://localhost:8089"

    class Config:
        env_file = ".env"


settings = Settings()
