"""Menu item unavailable exception."""

from fastapi import status

from .app_exception import AppException


class MenuItemUnavailableException(AppException):
    """Raised when an ordered item is not found in the menu or is inactive."""

    status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT
