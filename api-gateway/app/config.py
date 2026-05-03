"""
API Gateway configuration.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    USER_SERVICE_URL: str = "http://user-service:8001"
    JOB_SERVICE_URL: str = "http://job-service:8002"
    RECOMMENDATION_SERVICE_URL: str = "http://recommendation-service:8003"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    API_GATEWAY_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
