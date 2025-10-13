import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI CMS"
    DEBUG: bool = Field(False, env="DEBUG")

    # Database connection string (read from .env)
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # Security / JWT settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
