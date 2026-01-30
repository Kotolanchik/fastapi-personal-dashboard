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
    )
