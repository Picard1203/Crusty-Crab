"""Validation error."""

from fastapi import status

from .app_exception import AppException


class ValidationError(AppException):
    """Raised when business validation rules are violated."""

    status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT
