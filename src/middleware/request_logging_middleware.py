"""HTTP request/response logging middleware."""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs every incoming request and outgoing response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process a request and log the result.

        Args:
            request (Request): The incoming HTTP request.
            call_next (Callable): The next middleware or route handler.

        Returns:
            Response: The HTTP response.
        """
        start_time = time.perf_counter()
        logger.info(f"→ {request.method} {request.url.path}")
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"← {request.method} {request.url.path} "
            f"status={response.status_code} time={elapsed_ms:.1f}ms"
        )
        return response
