"""Order not modifiable exception."""

from fastapi import status

from .app_exception import AppException


class OrderNotModifiableException(AppException):
    """Raised when trying to update or delete a completed or cancelled order."""

    status_code: int = status.HTTP_409_CONFLICT
