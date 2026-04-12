"""Authorization exception."""

from fastapi import status

from .app_exception import AppException


class AuthorizationException(AppException):
    """Raised when a user lacks permission to perform an action."""

    status_code: int = status.HTTP_403_FORBIDDEN
