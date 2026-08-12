from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AgriSense AI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    FRONTEND_URL: str = ""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgrespassword@localhost:5432/agrisense"
    
    # Auth (Simple operator account)
    SECRET_KEY: str = "4f8a12b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # AI/Inference Configuration
    UPLOAD_DIR: str = "uploads"
    UPLOAD_MAX_MB: int = 100  # Maximum upload file size in megabytes
    ALLOWED_VIDEO_EXTENSIONS: frozenset = frozenset({".mp4", ".avi", ".mov", ".mkv", ".webm"})

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        placeholder = "change-this-to-a-very-secure-random-secret-key-in-production"
        if v == placeholder:
            raise ValueError(
                "SECRET_KEY is still set to the default placeholder. "
                "Generate a secure key with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if len(v) < 32:
            raise ValueError(
                f"SECRET_KEY is too short ({len(v)} chars). Minimum length is 32 characters."
            )
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
