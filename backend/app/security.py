from __future__ import annotations

import secrets
import time
from collections import defaultdict, deque
from threading import RLock
from uuid import uuid4

from fastapi import Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings


class RequestGuardMiddleware(BaseHTTPMiddleware):
    """Bound request sizes, throttle API clients, and add security headers."""

    def __init__(self, app) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = RLock()

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        supplied_request_id = request.headers.get("x-request-id", "")
        request_id = (
            supplied_request_id
            if supplied_request_id.isascii()
            and supplied_request_id.replace("-", "").replace("_", "").isalnum()
            and len(supplied_request_id) <= 64
            else uuid4().hex
        )
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                request_size = int(content_length)
            except ValueError:
                return self._error(
                    status.HTTP_400_BAD_REQUEST,
                    "INVALID_CONTENT_LENGTH",
                    "The Content-Length header must be an integer.",
                    request_id,
                )
            if request_size < 0 or request_size > settings.max_request_bytes:
                return self._error(
                    status.HTTP_413_CONTENT_TOO_LARGE,
                    "REQUEST_TOO_LARGE",
                    "The request body exceeds the configured limit.",
                    request_id,
                )
        if request.url.path.startswith("/api/") and not self._allow(request):
            return self._error(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "RATE_LIMITED",
                "Too many requests. Try again shortly.",
                request_id,
            )
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store"
        return response

    def _allow(self, request: Request) -> bool:
        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        cutoff = now - settings.rate_limit_window_seconds
        with self._lock:
            history = self._requests[client]
            while history and history[0] < cutoff:
                history.popleft()
            if len(history) >= settings.rate_limit_requests:
                return False
            history.append(now)
            return True

    @staticmethod
    def _error(
        status_code: int,
        code: str,
        message: str,
        request_id: str,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            headers={
                "X-Request-ID": request_id,
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
                "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
                "Cache-Control": "no-store",
            },
            content={
                "success": False,
                "error": {"code": code, "message": message},
            },
        )


def require_admin_key(x_admin_key: str | None = Header(default=None)) -> None:
    """Protect destructive operations when ADMIN_API_KEY is configured."""

    if not settings.admin_api_key:
        return
    if x_admin_key is None or not secrets.compare_digest(
        x_admin_key,
        settings.admin_api_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "ADMIN_AUTH_REQUIRED",
                "message": "A valid administrator key is required.",
            },
        )
