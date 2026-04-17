"""Invalid operation error."""

from fastapi import status

from .app_exception import AppException


class InvalidOperationError(AppException):
    """Raised when a requested operation is logically invalid."""

    status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT
