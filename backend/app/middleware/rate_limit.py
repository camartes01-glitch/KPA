"""
Rate Limiting Middleware — Production rate limiting with Redis & safe in-memory fallback.
Protects API against DoS and credential stuffing.
"""
import time
from collections import defaultdict
from typing import Dict, List, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

# In-memory sliding window fallback
_local_request_history: Dict[str, List[float]] = defaultdict(list)

# Lazy Redis client holder
_redis_client = None
_redis_checked = False


def _get_redis():
    global _redis_client, _redis_checked
    if not _redis_checked:
        _redis_checked = True
        if settings.REDIS_URL:
            try:
                import redis
                client = redis.from_url(settings.REDIS_URL, socket_timeout=1)
                client.ping()
                _redis_client = client
            except Exception:
                _redis_client = None
    return _redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_window: Optional[int] = None,
        window_seconds: Optional[int] = None,
    ):
        super().__init__(app)
        self.requests_per_window = requests_per_window or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        # Exclude probes, docs, static specs
        if (
            path in ("/health", "/api/v1/health", "/docs", "/redoc")
            or path.endswith("/openapi.json")
        ):
            return await call_next(request)

        # Identify client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        now = time.time()
        is_allowed = True
        remaining = self.requests_per_window

        r = _get_redis()
        if r is not None:
            try:
                key = f"rate_limit:{client_ip}:{int(now // self.window_seconds)}"
                current_count = r.incr(key)
                if current_count == 1:
                    r.expire(key, self.window_seconds)
                if current_count > self.requests_per_window:
                    is_allowed = False
                remaining = max(0, self.requests_per_window - current_count)
            except Exception:
                r = None  # Fallback to local memory if redis fails

        if r is None:
            # In-memory sliding window
            history = _local_request_history[client_ip]
            cutoff = now - self.window_seconds
            # Purge expired timestamps
            _local_request_history[client_ip] = [t for t in history if t > cutoff]
            history = _local_request_history[client_ip]
            if len(history) >= self.requests_per_window:
                is_allowed = False
            else:
                history.append(now)
            remaining = max(0, self.requests_per_window - len(history))

        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Too many requests. Please wait a moment and try again.",
                    "detail": "Rate limit exceeded. Try again in 60 seconds.",
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.requests_per_window),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
