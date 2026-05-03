"""
Job Service configuration.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URL: str = "mongodb://localhost:27017"
    MONGO_DB: str = "job_recommendation"
    REDIS_URL: str = "redis://localhost:6379"
    LOG_LEVEL: str = "INFO"
    JOB_SERVICE_PORT: int = 8002

    class Config:
        env_file = ".env"


settings = Settings()
