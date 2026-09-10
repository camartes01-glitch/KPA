"""
Application Configuration — loaded from environment variables.
Never hardcode secrets here.
"""
from typing import List
from functools import lru_cache

from pydantic import AnyHttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ─────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_NAME: str = "KPA Welfare Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── API ─────────────────────────────────────────────────────────────────
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    ALLOWED_HOSTS: List[str] = ["*"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = "changeme-development-only-replace-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://kpa_user:kpa_password@localhost:5432/kpa_db"
    DATABASE_SYNC_URL: str = "postgresql://kpa_user:kpa_password@localhost:5432/kpa_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40

    # ── Redis ────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── OTP ──────────────────────────────────────────────────────────────────
    OTP_EXPIRY_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RATE_LIMIT_PER_HOUR: int = 10
    OTP_DEV_MODE: bool = True
    OTP_DEV_FIXED_CODE: str = "123456"

    # ── Google OAuth ─────────────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_GMAIL_ONLY: bool = True

    # ── Supabase Storage ─────────────────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_BUCKET_MEMBERS: str = "kpa-members"
    SUPABASE_BUCKET_WELFARE: str = "kpa-welfare"

    # ── Razorpay ─────────────────────────────────────────────────────────────
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    RAZORPAY_AUTOPAY_MAX_AMOUNT: int = 1000  # paise

    # ── Cashfree ─────────────────────────────────────────────────────────────
    CASHFREE_APP_ID: str = ""
    CASHFREE_SECRET_KEY: str = ""
    CASHFREE_WEBHOOK_SECRET: str = ""
    CASHFREE_ENVIRONMENT: str = "TEST"

    # ── Firebase ─────────────────────────────────────────────────────────────
    FIREBASE_SERVICE_ACCOUNT_PATH: str = ""
    FIREBASE_SERVICE_ACCOUNT_JSON: str = ""

    # ── SMS ──────────────────────────────────────────────────────────────────
    SMS_PROVIDER: str = "msg91"
    MSG91_AUTH_KEY: str = ""
    MSG91_SENDER_ID: str = "KPAWEL"
    MSG91_TEMPLATE_OTP: str = ""
    MSG91_TEMPLATE_WELFARE: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""

    # ── Email ────────────────────────────────────────────────────────────────
    EMAIL_PROVIDER: str = "sendgrid"
    EMAIL_FROM_ADDRESS: str = "noreply@kpawelfare.org"
    EMAIL_FROM_NAME: str = "KPA Welfare"
    SENDGRID_API_KEY: str = ""
    RESEND_API_KEY: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True

    # ── File Upload ──────────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    @field_validator("ALLOWED_IMAGE_TYPES", mode="before")
    @classmethod
    def split_image_types(cls, v):
        if isinstance(v, str):
            return [t.strip() for t in v.split(",")]
        return v

    # ── Rate Limiting ────────────────────────────────────────────────────────
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── Logging ──────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # ── Monitoring ───────────────────────────────────────────────────────────
    SENTRY_DSN: str = ""

    # ── Computed properties ──────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @model_validator(mode="after")
    def validate_production_safety(self) -> "Settings":
        if self.APP_ENV == "production":
            if self.SECRET_KEY == "changeme-development-only-replace-in-production" or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "Production safety violation: SECRET_KEY must be set to a secure string with at least 32 characters in production."
                )
            if not self.GOOGLE_CLIENT_ID:
                raise ValueError(
                    "Production safety violation: GOOGLE_CLIENT_ID must be configured in production."
                )
            if self.OTP_DEV_MODE:
                object.__setattr__(self, "OTP_DEV_MODE", False)
        return self



@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
