"""Business logic for menu item operations."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from src.exceptions import DuplicateError, NotFoundError
from src.factories import MenuItemFactory
from src.models import MenuItemDocument
from src.repositories import MenuItemRepository
from src.schemas import MenuItemCreate, MenuItemUpdate, PaginatedResponse

logger = logging.getLogger(__name__)


class MenuItemService:
    """Orchestrates menu item business logic.

    Attributes:
        _repository (MenuItemRepository): Menu item data access.
        _factory (MenuItemFactory): Document construction.
    """

    def __init__(
        self,
        repository: MenuItemRepository,
        factory: MenuItemFactory,
    ) -> None:
        """Initialize with repository and factory dependencies.

        Args:
            repository (MenuItemRepository): The menu item repository interface.
            factory (MenuItemFactory): The menu item document factory.
        """
        self._repository: MenuItemRepository = repository
        self._factory: MenuItemFactory = factory

    async def get_menu_item(self, item_number: int) -> MenuItemDocument:
        """Retrieve a single menu item by its number.

        Args:
            item_number (int): The auto-increment menu item identifier.

        Returns:
            MenuItemDocument: The found menu item.

        Raises:
            NotFoundError: If no menu item exists with this number.
        """
        logger.info(f"Fetching menu item {item_number}")
        item = await self._repository.get_by_item_number(item_number)
        if item is None:
            raise NotFoundError(
                f"Menu item with number {item_number} not found"
            )
        return item

    async def get_active_menu(self) -> List[MenuItemDocument]:
        """Retrieve all currently active menu items.

        Returns:
            List[MenuItemDocument]: All menu items available for ordering.
        """
        logger.info("Fetching active menu")
        return await self._repository.get_active_items()

    async def get_all_menu_items(
        self, skip: int, limit: int
    ) -> PaginatedResponse[MenuItemDocument]:
        """Retrieve a paginated list of all menu items.

        Args:
            skip (int): Number of documents to skip.
            limit (int): Maximum number of documents to return.

        Returns:
            PaginatedResponse[MenuItemDocument]: Paginated results.
        """
        logger.info(f"Listing menu items skip={skip} limit={limit}")
        items = await self._repository.get_all(skip, limit, {})
        total = await self._repository.count({})
        return PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total,
        )

    async def create_menu_item(self, data: MenuItemCreate) -> MenuItemDocument:
        """Create a new menu item after validating name uniqueness.

        Args:
            data (MenuItemCreate): The validated creation request.

        Returns:
            MenuItemDocument: The persisted menu item document.

        Raises:
            DuplicateError: If a menu item with this name already exists.
        """
        logger.info(f"Creating menu item '{data.name}'")
        existing = await self._repository.get_by_name(data.name)
        if existing is not None:
            raise DuplicateError(
                f"Menu item with name '{data.name}' already exists"
            )
        item = await self._factory.create(data)
        return await self._repository.create(item)

    async def update_menu_item(
        self, item_number: int, data: MenuItemUpdate
    ) -> MenuItemDocument:
        """Update an existing menu item.

        Args:
            item_number (int): The business ID of the menu item to update.
            data (MenuItemUpdate): The validated update request.

        Returns:
            MenuItemDocument: The updated menu item document.

        Raises:
            NotFoundError: If no menu item exists with this number.
            DuplicateError: If the updated name conflicts with an existing item.
        """
        logger.info(f"Updating menu item {item_number}")
        item = await self._get_existing_item(item_number)
        update_data: Dict[str, Any] = data.model_dump(exclude_none=True)
        if "name" in update_data:
            await self._ensure_name_uniqueness(item.id, update_data["name"])
        update_data["updated_at"] = datetime.now(timezone.utc)
        return await self._apply_update(item.id, update_data)

    async def delete_menu_item(self, item_number: int) -> None:
        """Soft-delete a menu item by marking it inactive.

        Args:
            item_number (int): The business ID of the menu item to deactivate.

        Raises:
            NotFoundError: If no menu item exists with this number.
        """
        logger.info(f"Soft-deleting menu item {item_number}")
        item = await self._get_existing_item(item_number)
        update_data: Dict[str, Any] = {
            "is_active": False,
            "updated_at": datetime.now(timezone.utc),
        }
        await self._repository.update(item.id, update_data)

    async def _get_existing_item(self, item_number: int) -> MenuItemDocument:
        """Fetch a menu item by business number or raise if not found.

        Args:
            item_number (int): The menu item business identifier.

        Returns:
            MenuItemDocument: The found menu item document.

        Raises:
            NotFoundError: If no item exists with the given number.
        """
        item = await self._repository.get_by_item_number(item_number)
        if item is None:
            raise NotFoundError(
                f"Menu item with number {item_number} not found"
            )
        return item

    async def _ensure_name_uniqueness(
        self, internal_id: Any, name: str
    ) -> None:
        """Validate that the provided name is not taken by another item.

        Args:
            internal_id (Any): The internal database ID of the item being updated.
            name (str): The new name to check for duplicates.

        Raises:
            DuplicateError: If another menu item with the same name exists.
        """
        existing = await self._repository.get_by_name(name)
        if (existing is not None) and (existing.id != internal_id):
            raise DuplicateError(f"Menu item with name '{name}' already exists")

    async def _apply_update(
        self, internal_id: Any, update_data: Dict[str, Any]
    ) -> MenuItemDocument:
        """Commit the update to the repository.

        Args:
            internal_id (Any): The internal database ID.
            update_data (Dict[str, Any]): The fields and values to update.

        Returns:
            MenuItemDocument: The updated menu item document.

        Raises:
            NotFoundError: If the update fails because the record was
                not found.
        """
        updated = await self._repository.update(internal_id, update_data)
        if updated is None:
            raise NotFoundError("Menu item record missing during update")
        return updated
