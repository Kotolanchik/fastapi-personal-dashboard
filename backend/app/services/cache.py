import json
from functools import lru_cache
from typing import Any, Optional

from redis import Redis
from redis.exceptions import RedisError

from ..core.config import get_settings


@lru_cache
def get_cache_client() -> Optional[Redis]:
    settings = get_settings()
    if not settings.redis_url:
        return None
    try:
        return Redis.from_url(settings.redis_url, decode_responses=True)
    except RedisError:
        return None


def get_json(key: str) -> Optional[dict[str, Any]]:
    client = get_cache_client()
    if not client:
        return None
    try:
        value = client.get(key)
    except RedisError:
        return None
    if not value:
        return None
    return json.loads(value)


def set_json(key: str, payload: dict[str, Any], ttl_seconds: int) -> None:
    client = get_cache_client()
    if not client:
        return
    try:
        client.setex(key, ttl_seconds, json.dumps(payload))
    except RedisError:
        return
