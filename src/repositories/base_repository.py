"""Abstract base repository defining the universal CRUD contract."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.models.base_document import BaseDocument


class BaseRepository(ABC):
    """Abstract base repository with universal CRUD operations."""

    @abstractmethod
    async def get_all(
        self, skip: int, limit: int, filters: Dict[str, Any]
    ) -> List[BaseDocument]:
        """Retrieve entities with pagination and filtering.

        Args:
            skip (int): Number of documents to skip.
            limit (int): Maximum number of documents to return.
            filters (Dict[str, Any]): Key-value pairs for query filtering.

        Returns:
            List[BaseDocument]: The matching entities.
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, entity: BaseDocument) -> BaseDocument:
        """Persist a new entity to the database.

        Args:
            entity (BaseDocument): The document to insert.

        Returns:
            BaseDocument: The inserted document with _id populated.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, entity_id: Any, data: Dict[str, Any]
    ) -> Optional[BaseDocument]:
        """Update an existing entity by its identifier.

        Args:
            entity_id (Any): The entity identifier.
            data (Dict[str, Any]): Fields to update with their new values.

        Returns:
            Optional[BaseDocument]: The updated entity if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity_id: Any) -> bool:
        """Delete an entity by its identifier.

        Args:
            entity_id (Any): The entity identifier.

        Returns:
            bool: True if deleted, False if not found.
        """
        raise NotImplementedError

    @abstractmethod
    async def count(self, filters: Dict[str, Any]) -> int:
        """Count entities matching the given filters.

        Args:
            filters (Dict[str, Any]): Key-value pairs for query filtering.

        Returns:
            int: Number of matching entities.
        """
        raise NotImplementedError
