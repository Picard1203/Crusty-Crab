"""Concrete MongoDB implementation of the menu item repository."""

import logging
from typing import Any, Dict, List, Optional

from bson import ObjectId

from src.models import MenuItemDocument
from src.repositories import MenuItemRepository

logger = logging.getLogger(__name__)


class MongoMenuItemRepository(MenuItemRepository):
    """Beanie-based implementation of MenuItemRepository."""

    async def get_by_id(
        self, entity_id: ObjectId
    ) -> Optional[MenuItemDocument]:
        """Retrieve a menu item by MongoDB ObjectId.

        Args:
            entity_id (ObjectId): The MongoDB document ID.

        Returns:
            Optional[MenuItemDocument]: The item if found, None otherwise.
        """
        logger.debug(f"Fetching menu item by ObjectId {entity_id}")
        return await MenuItemDocument.get(entity_id)

    async def get_by_item_number(
        self, item_number: int
    ) -> Optional[MenuItemDocument]:
        """Retrieve a menu item by its auto-increment number.

        Args:
            item_number (int): The unique menu item identifier.

        Returns:
            Optional[MenuItemDocument]: The item if found, None otherwise.
        """
        logger.debug(f"Fetching menu item by item_number {item_number}")
        return await MenuItemDocument.find_one(
            MenuItemDocument.item_number == item_number
        )

    async def get_by_name(self, name: str) -> Optional[MenuItemDocument]:
        """Retrieve a menu item by its exact display name.

        Args:
            name (str): The menu item name.

        Returns:
            Optional[MenuItemDocument]: The item if found, None otherwise.
        """
        logger.debug(f"Fetching menu item by name '{name}'")
        return await MenuItemDocument.find_one(
            MenuItemDocument.name == name
        )

    async def get_active_items(self) -> List[MenuItemDocument]:
        """Retrieve all menu items that are currently active.

        Returns:
            List[MenuItemDocument]: All items where is_active is True.
        """
        logger.debug("Fetching all active menu items")
        return await MenuItemDocument.find(
            MenuItemDocument.is_active == True  # noqa: E712
        ).to_list()

    async def get_all(
        self, skip: int, limit: int, filters: Dict[str, Any]
    ) -> List[MenuItemDocument]:
        """Retrieve menu items with pagination and filtering.

        Args:
            skip (int): Number of documents to skip.
            limit (int): Maximum number of documents to return.
            filters (Dict[str, Any]): Key-value pairs for query filtering.

        Returns:
            List[MenuItemDocument]: The matching menu items.
        """
        query = self._build_query(filters)
        logger.debug(
            f"Querying menu items with filters {filters}, "
            f"skip={skip}, limit={limit}"
        )
        return (
            await MenuItemDocument.find(query)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def create(self, entity: MenuItemDocument) -> MenuItemDocument:
        """Persist a new menu item document to MongoDB.

        Args:
            entity (MenuItemDocument): The document to insert.

        Returns:
            MenuItemDocument: The inserted document with _id populated.
        """
        logger.info(
            f"Creating menu item '{entity.name}' "
            f"with item_number {entity.item_number}"
        )
        await entity.insert()
        return entity

    async def update(
        self, entity_id: ObjectId, data: Dict[str, Any]
    ) -> Optional[MenuItemDocument]:
        """Update an existing menu item by ObjectId.

        Args:
            entity_id (ObjectId): The MongoDB document ID.
            data (Dict[str, Any]): Fields to update with their new values.

        Returns:
            Optional[MenuItemDocument]: The updated item, None if not found.
        """
        logger.info(
            f"Updating menu item {entity_id} with fields {list(data.keys())}"
        )
        item = await MenuItemDocument.get(entity_id)
        if item is None:
            return None
        await item.set(data)
        return item

    async def delete(self, entity_id: ObjectId) -> bool:
        """Delete a menu item by ObjectId.

        Args:
            entity_id (ObjectId): The MongoDB document ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        logger.info(f"Deleting menu item {entity_id}")
        item = await MenuItemDocument.get(entity_id)
        if item is None:
            return False
        await item.delete()
        return True

    async def count(self, filters: Dict[str, Any]) -> int:
        """Count menu items matching the given filters.

        Args:
            filters (Dict[str, Any]): Key-value pairs for query filtering.

        Returns:
            int: Number of matching menu items.
        """
        query = self._build_query(filters)
        return await MenuItemDocument.find(query).count()

    @staticmethod
    def _build_query(filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build a MongoDB query dict from filter parameters.

        Args:
            filters (Dict[str, Any]): Raw filter key-value pairs.

        Returns:
            Dict[str, Any]: MongoDB-compatible query dictionary.
        """
        query: Dict[str, Any] = {}
        if filters.get("is_active") is not None:
            query["is_active"] = filters["is_active"]
        name = filters.get("name")
        if name is not None:
            query["name"] = {"$regex": name, "$options": "i"}
        return query
