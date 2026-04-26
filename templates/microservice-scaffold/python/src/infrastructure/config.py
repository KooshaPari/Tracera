"""Configuration management."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    service_name: str = "microservice"
    http_port: int = 8080
    database_url: str = "postgresql+asyncpg://localhost:5432/microservice"
    nats_url: str = "nats://localhost:4222"
    otel_endpoint: str = "localhost:4317"
    environment: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
