"""
Simple Redis cache-aside helpers for product detail and price summaries.
Source of truth remains PostgreSQL. Fail-open on Redis errors.
"""
from __future__ import annotations
import json
import logging
from typing import Any, Optional
from app.core.config import settings

logger = logging.getLogger("priceloop.cache")
_redis = None

DEFAULT_TTL_PRODUCT = 120  # seconds
DEFAULT_TTL_PRICES = 60
DEFAULT_TTL_ANALYTICS = 90

def _client():
    global _redis
    if _redis is not None:
        return _redis
    try:
        import redis
        _redis = redis.from_url(settings.redis_url, socket_connect_timeout=1.5, socket_timeout=1.5, decode_responses=True)
        _redis.ping()
        return _redis
    except Exception as exc:
        logger.warning("Cache: Redis unavailable (%s)", type(exc).__name__)
        _redis = None
        return None

def cache_get(key: str) -> Optional[Any]:
    r = _client()
    if not r:
        return None
    try:
        raw = r.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.warning("cache_get failed: %s", type(exc).__name__)
        return None

def cache_set(key: str, value: Any, ttl: int = 60) -> None:
    r = _client()
    if not r:
        return
    try:
        r.setex(key, ttl, json.dumps(value, default=str))
    except Exception as exc:
        logger.warning("cache_set failed: %s", type(exc).__name__)

def cache_delete_prefix(prefix: str) -> None:
    r = _client()
    if not r:
        return
    try:
        keys = list(r.scan_iter(match=f"{prefix}*", count=100))
        if keys:
            r.delete(*keys)
    except Exception as exc:
        logger.warning("cache_delete_prefix failed: %s", type(exc).__name__)

def product_key(product_id: str) -> str:
    return f"cache:product:{product_id}"

def prices_key(product_id: str, limit: int) -> str:
    return f"cache:prices:{product_id}:{limit}"

def analytics_key(product_id: str, days: int) -> str:
    return f"cache:analytics:{product_id}:{days}"
