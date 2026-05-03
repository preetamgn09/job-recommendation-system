"""
User Service configuration — reads from environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URL: str = "mongodb://localhost:27017"
    MONGO_DB: str = "job_recommendation"
    REDIS_URL: str = "redis://localhost:6379"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    LOG_LEVEL: str = "INFO"
    USER_SERVICE_PORT: int = 8001

    class Config:
        env_file = ".env"


settings = Settings()
