"""Authentication error."""

from fastapi import status

from .app_exception import AppException


class AuthenticationError(AppException):
    """Raised when authentication credentials are invalid or missing."""

    status_code: int = status.HTTP_401_UNAUTHORIZED
