"""
Redis-backed fixed-window rate limiter for FastAPI.
Fail-open on Redis errors. Returns 429 + Retry-After when exceeded.
"""
from __future__ import annotations
import logging
from typing import Callable
from fastapi import HTTPException, Request, status
from app.core.config import settings

logger = logging.getLogger("priceloop.rate_limit")
_redis = None

def _get_redis():
    global _redis
    if _redis is not None:
        return _redis
    try:
        import redis
        _redis = redis.from_url(settings.redis_url, socket_connect_timeout=1.5, socket_timeout=1.5, decode_responses=True)
        _redis.ping()
        return _redis
    except Exception as exc:
        logger.warning("Rate limiter: Redis unavailable (%s); fail-open", type(exc).__name__)
        _redis = None
        return None

def _client_key(request: Request, prefix: str, per_user: bool = False) -> str:
    user_part = "anon"
    if per_user:
        auth = request.headers.get("Authorization") or ""
        if auth.lower().startswith("bearer ") and len(auth) > 20:
            user_part = f"tok:{auth[7:27]}"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded and settings.environment == "production":
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    return f"rl:{prefix}:{user_part}:{ip}"

def rate_limit(*, max_requests: int, window_seconds: int, prefix: str, per_user: bool = False) -> Callable:
    def dependency(request: Request) -> None:
        r = _get_redis()
        if r is None:
            return
        key = _client_key(request, prefix, per_user=per_user)
        try:
            count = r.incr(key)
            if count == 1:
                r.expire(key, window_seconds)
            if count > max_requests:
                ttl = r.ttl(key)
                retry_after = ttl if ttl and ttl > 0 else window_seconds
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={"error": {"code": "RATE_LIMIT_EXCEEDED", "message": f"Too many requests. Try again in {retry_after} seconds."}},
                    headers={"Retry-After": str(retry_after)},
                )
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning("Rate limiter error (%s); fail-open", type(exc).__name__)
    return dependency

limit_login = rate_limit(max_requests=5, window_seconds=60, prefix="login")
limit_register = rate_limit(max_requests=3, window_seconds=60, prefix="register")
limit_products_write = rate_limit(max_requests=30, window_seconds=60, prefix="products_write", per_user=True)
limit_products_read = rate_limit(max_requests=120, window_seconds=60, prefix="products_read", per_user=True)
limit_scrape_trigger = rate_limit(max_requests=10, window_seconds=60, prefix="scrape", per_user=True)
