import os
from dataclasses import dataclass
from functools import lru_cache


def _parse_list(value: str) -> list[str]:
    if not value or value.strip() == "*":
        return ["*"]
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    database_url: str
    cors_origins: list[str]
    environment: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    auto_create_tables: bool
    redis_url: str | None
    cache_ttl_seconds: int
    llm_api_key: str | None
    llm_base_url: str | None
    llm_model: str
    # Integrations: Google Fit OAuth
    google_client_id: str | None
    google_client_secret: str | None
    google_redirect_uri: str | None
    google_oauth_auth_url: str
    google_oauth_token_url: str
    fitness_aggregate_url: str
    # Import: max file size (bytes) for Apple Health / uploads
    max_import_file_size_bytes: int
    # Sync rate limit: min seconds between syncs per source
    sync_min_interval_seconds: int
    # Global API rate limit per IP (e.g. "200/minute" for slowapi default_limits)
    rate_limit_default: str
    # Notifications: email reminders (optional)
    smtp_host: str | None
    smtp_port: int
    smtp_user: str | None
    smtp_password: str | None
    smtp_from_email: str | None


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./data/app.db"),
        cors_origins=_parse_list(os.getenv("CORS_ORIGINS", "*")),
        environment=os.getenv("APP_ENV", "local"),
        secret_key=os.getenv("SECRET_KEY", "change-me"),
        algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")),
        auto_create_tables=_parse_bool(os.getenv("AUTO_CREATE_TABLES"), default=False),
        redis_url=os.getenv("REDIS_URL"),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
        llm_api_key=os.getenv("LLM_API_KEY") or None,
        llm_base_url=os.getenv("LLM_BASE_URL") or None,
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        google_client_id=os.getenv("GOOGLE_CLIENT_ID") or None,
        google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET") or None,
        google_redirect_uri=os.getenv("GOOGLE_REDIRECT_URI") or None,
        google_oauth_auth_url=os.getenv("GOOGLE_OAUTH_AUTH_URL", "https://accounts.google.com/o/oauth2/v2/auth"),
        google_oauth_token_url=os.getenv("GOOGLE_OAUTH_TOKEN_URL", "https://oauth2.googleapis.com/token"),
        fitness_aggregate_url=os.getenv(
            "FITNESS_AGGREGATE_URL",
            "https://fitness.googleapis.com/fitness/v1/users/me/dataset:aggregate",
        ),
        max_import_file_size_bytes=int(os.getenv("MAX_IMPORT_FILE_SIZE_MB", "100")) * 1024 * 1024,
        sync_min_interval_seconds=int(os.getenv("SYNC_MIN_INTERVAL_SECONDS", "900")),  # 15 min
        rate_limit_default=os.getenv("RATE_LIMIT_DEFAULT", "200/minute"),
        smtp_host=os.getenv("SMTP_HOST") or None,
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER") or None,
        smtp_password=os.getenv("SMTP_PASSWORD") or None,
        smtp_from_email=os.getenv("SMTP_FROM_EMAIL") or None,
    )
