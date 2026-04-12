"""Invalid status transition exception."""

from fastapi import status

from .app_exception import AppException


class InvalidStatusTransitionException(AppException):
    """Raised when a worker attempts a disallowed order status transition."""

    status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT
