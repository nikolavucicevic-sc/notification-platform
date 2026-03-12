from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    rabbitmq_url: str
    rabbitmq_email_queue: str = "email.send"
    rabbitmq_status_queue: str = "email.status"
    wiremock_url: str = "http://localhost:8089"

    class Config:
        env_file = ".env"


settings = Settings()
