"""Abstract database interface."""

from abc import ABC, abstractmethod
from typing import Any


class Database(ABC):
    """Abstract base class for database connections."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish a connection to the database."""
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection to the database."""
        raise NotImplementedError

    @abstractmethod
    async def init_models(self) -> None:
        """Register Beanie document models with the database."""
        raise NotImplementedError

    @abstractmethod
    async def get_session(self) -> Any:
        """Get a database session for performing operations.

        Returns:
            Any: A database session object for transactional operations.
        """
        raise NotImplementedError
