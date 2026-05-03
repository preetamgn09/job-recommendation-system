"""
API Gateway — middleware for logging, metrics, and CORS.
"""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status, and duration."""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)

        # Skip static file logs
        path = request.url.path
        if not path.startswith("/static"):
            print(
                f"🌐 {request.method} {path} → {response.status_code} ({duration_ms}ms)"
            )

        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        return response
