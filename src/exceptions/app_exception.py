"""Base application exception for domain error hierarchy."""

from __future__ import annotations

from abc import ABC

from fastapi import status


class AppException(ABC, Exception):
    """Abstract base for all domain exceptions.

    Attributes:
        message (str): Human-readable error description.
        status_code (int): HTTP status code for the response.
        path (str): Dot-separated inheritance chain (e.g.
            ``AppException.NotFoundError``).
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        """Initialize with an error message.

        Args:
            message (str): Human-readable error description.
        """
        self.message: str = message
        super().__init__(message)

    @property
    def path(self) -> str:
        """Return the dot-separated class hierarchy path.

        Returns:
            str: Inheritance chain from AppException to the concrete type.
        """
        chain = [
            cls.__name__
            for cls in reversed(type(self).__mro__)
            if issubclass(cls, AppException)
        ]
        return ".".join(chain)
