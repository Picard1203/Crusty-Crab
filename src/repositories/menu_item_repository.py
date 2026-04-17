"""Abstract menu item repository with domain-specific query methods."""

from abc import abstractmethod
from typing import List, Optional

from src.models.menu_item_document import MenuItemDocument
from src.repositories.base_repository import BaseRepository


class MenuItemRepository(BaseRepository):
    """Extends BaseRepository with menu-item-specific access patterns."""

    @abstractmethod
    async def get_by_item_number(
        self, item_number: int
    ) -> Optional[MenuItemDocument]:
        """Retrieve a menu item by its auto-increment number.

        Args:
            item_number (int): The unique menu item identifier.

        Returns:
            Optional[MenuItemDocument]: The item if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[MenuItemDocument]:
        """Retrieve a menu item by its exact display name.

        Args:
            name (str): The menu item name.

        Returns:
            Optional[MenuItemDocument]: The item if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_active_items(self) -> List[MenuItemDocument]:
        """Retrieve all menu items that are currently active.

        Returns:
            List[MenuItemDocument]: All items where is_active is True.
        """
        raise NotImplementedError
