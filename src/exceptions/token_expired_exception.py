"""Token expired exception."""

from fastapi import status

from .app_exception import AppException


class TokenExpiredException(AppException):
    """Raised when a JWT token has expired."""

    status_code: int = status.HTTP_401_UNAUTHORIZED
