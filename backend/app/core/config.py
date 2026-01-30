import os
from dataclasses import dataclass
from functools import lru_cache


def _parse_list(value: str) -> list[str]:
    if not value or value.strip() == "*":
        return ["*"]
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    database_url: str
    cors_origins: list[str]
    environment: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./data/app.db"),
        cors_origins=_parse_list(os.getenv("CORS_ORIGINS", "*")),
        environment=os.getenv("APP_ENV", "local"),
    )
