"""Base application exception for domain error hierarchy."""

from abc import ABC

from fastapi import status


class AppException(ABC, Exception):
    """Abstract base for all domain exceptions.

    Attributes:
        message (str): Human-readable error description.
        status_code (int): HTTP status code for the response.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        """Initialize with an error message.

        Args:
            message (str): Human-readable error description.
        """
        self.message: str = message
        super().__init__(message)
