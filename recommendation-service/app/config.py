"""
Recommendation Service configuration.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URL: str = "mongodb://localhost:27017"
    MONGO_DB: str = "job_recommendation"
    REDIS_URL: str = "redis://localhost:6379"
    LOG_LEVEL: str = "INFO"
    RECOMMENDATION_SERVICE_PORT: int = 8003
    JOB_SERVICE_URL: str = "http://job-service:8002"
    USER_SERVICE_URL: str = "http://user-service:8001"
    RECO_TOP_N: int = 10
    RECO_CONTENT_WEIGHT: float = 0.7
    RECO_ACTIVITY_WEIGHT: float = 0.3
    REDIS_TTL: int = 300

    class Config:
        env_file = ".env"


settings = Settings()
