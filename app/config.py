from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache
import json
from pydantic import computed_field
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gomaflex"
    
    # App
    APP_NAME: str = "GOMAFLEX Backend"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    API_TOKEN: str = "gomaflex-frontend-secret-token-2024"
    
    # CORS - parse JSON string from env or use default list
    CORS_ORIGINS_RAW: str = '["http://localhost:5173","http://localhost:8080","http://127.0.0.1:5173","https://gomaflex.duckdns.org","https://www.gomaflex.duckdns.org"]'
    
    # Email (para paso posterior)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "GOMAFLEX <noreply@gomaflex.com>"
    EMAIL_TO: str = "alexjhoan.25@gmail.com"

    @computed_field
    @property
    def cors_origins(self) -> List[str]:
        try:
            return json.loads(self.CORS_ORIGINS_RAW)
        except (json.JSONDecodeError, TypeError):
            return [
                "http://localhost:5173", 
                "http://localhost:8080", 
                "http://127.0.0.1:5173",
                "https://gomaflex.duckdns.org",
                "https://www.gomaflex.duckdns.org"
            ]

    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = True,
        extra = "ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()