"""Abstract base factory for constructing Beanie documents."""

from abc import ABC, abstractmethod
from typing import Any

from src.models import BaseDocument
from src.schemas.base_request import BaseRequest


class DocumentFactory(ABC):
    """Abstract factory defining the document construction contract."""

    @abstractmethod
    async def create(self, data: BaseRequest, **kwargs: Any) -> BaseDocument:
        """Construct a new document from request data.

        Args:
            data (BaseRequest): The validated request schema.
            **kwargs (Any): Additional context needed for construction.

        Returns:
            BaseDocument: The constructed document, ready for persistence.

        Raises:
            NotImplementedError: If the subclass does not implement this.
        """
        raise NotImplementedError
