"""Validation exception."""

from fastapi import status

from .app_exception import AppException


class ValidationException(AppException):
    """Raised when business validation rules are violated."""

    status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT
