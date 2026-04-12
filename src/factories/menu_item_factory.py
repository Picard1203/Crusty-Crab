"""Factory for constructing MenuItemDocument instances."""

import logging
from datetime import datetime, timezone
from typing import Any

from src.constants.sequence_constants import MENU_ITEM_NUMBER_SEQUENCE
from src.factories.document_factory import DocumentFactory
from src.models import MenuItemDocument
from src.repositories import CounterRepository
from src.schemas import MenuItemCreate

logger = logging.getLogger(__name__)


class MenuItemFactory(DocumentFactory):
    """Constructs MenuItemDocument instances with auto-increment IDs.

    Attributes:
        _counter_repo (CounterRepository): Repository for atomic ID generation.
    """

    def __init__(self, counter_repo: CounterRepository) -> None:
        """Initialize with a counter repository dependency.

        Args:
            counter_repo (CounterRepository): For generating auto-increment IDs.
        """
        self._counter_repo: CounterRepository = counter_repo

    async def create(
        self,
        data: MenuItemCreate,
        **kwargs: Any,  # noqa: ARG002
    ) -> MenuItemDocument:
        """Construct a new MenuItemDocument from creation request data.

        Args:
            data (MenuItemCreate): The validated menu item creation schema.
            **kwargs (Any): Not used. Present for ABC compliance.

        Returns:
            MenuItemDocument: The constructed document, ready for persistence.
        """
        item_number = await self._counter_repo.get_next_sequence(
            MENU_ITEM_NUMBER_SEQUENCE
        )
        now = datetime.now(timezone.utc)
        logger.info(
            f"Constructing menu item document with item_number {item_number}"
        )
        return MenuItemDocument(
            item_number=item_number,
            name=data.name,
            price=data.price,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
