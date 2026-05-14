from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./job_tracker_dev.db"
    environment: str = "development"
    debug: bool = True
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 1440
    frontend_url: str = "http://localhost:3000"
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_redirect_uri: str = "http://localhost:8000/api/email/gmail/callback"
    email_token_encryption_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("allowed_origins")
    @classmethod
    def normalize_origins(cls, value: str) -> str:
        return value.strip()

    @property
    def origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def gmail_oauth_configured(self) -> bool:
        return bool(self.gmail_client_id and self.gmail_client_secret and self.gmail_redirect_uri)


@lru_cache
def get_settings() -> Settings:
    return Settings()
