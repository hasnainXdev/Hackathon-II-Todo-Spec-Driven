import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, validator
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Todo API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database settings
    DATABASE_URL: str | None = None

    # JWT settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Better Auth settings
    BETTER_AUTH_SECRET: str | None = None
    BETTER_AUTH_URL: str | None = None

    # AI Service settings
    GEMINI_API_KEY: str | None = None
    OPEN_ROUTER_KEY: str | None = None
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 1000

    model_config = ConfigDict(case_sensitive=True)


settings = Settings()
