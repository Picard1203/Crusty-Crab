"""Not found error."""

from fastapi import status

from .app_exception import AppException


class NotFoundError(AppException):
    """Raised when a requested resource cannot be found."""

    status_code: int = status.HTTP_404_NOT_FOUND
