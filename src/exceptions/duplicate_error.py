"""Duplicate resource error."""

from fastapi import status

from .app_exception import AppException


class DuplicateError(AppException):
    """Raised when a resource with conflicting unique fields already exists."""

    status_code: int = status.HTTP_409_CONFLICT
