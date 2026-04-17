"""Integration tests for MongoMenuItemRepository."""

from datetime import datetime, timezone

import pytest

from src.models.menu_item_document import MenuItemDocument
from src.repositories.mongodb.mongo_menu_item_repository import (
    MongoMenuItemRepository,
)


async def _insert_item(
    repo: MongoMenuItemRepository,
    item_number: int = 1,
    name: str = "Schnitzel Alef",
    price: float = 66.0,
    is_active: bool = True,
) -> MenuItemDocument:
    """Insert a menu item document directly into the repository.

    Args:
        repo (MongoMenuItemRepository): The repository.
        item_number (int): The menu item number.
        name (str): The item name.
        price (float): The item price.
        is_active (bool): Whether the item is active.

    Returns:
        MenuItemDocument: The inserted document.
    """
    now = datetime.now(timezone.utc)
    item = MenuItemDocument(
        item_number=item_number,
        name=name,
        price=price,
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )
    return await repo.create(item)


@pytest.mark.asyncio
class TestMenuItemRepository:
    """Tests for MongoMenuItemRepository against real MongoDB."""

    async def test_create_and_get_by_id(self) -> None:
        """Created item is retrievable by ObjectId."""
        repo = MongoMenuItemRepository()
        item = await _insert_item(repo)
        found = await repo.get_by_id(item.id)
        assert found is not None
        assert found.item_number == 1

    async def test_get_by_item_number(self) -> None:
        """Item is retrievable by business item number."""
        repo = MongoMenuItemRepository()
        await _insert_item(repo, item_number=42)
        found = await repo.get_by_item_number(42)
        assert found is not None
        assert found.item_number == 42

    async def test_get_by_name(self) -> None:
        """Item is retrievable by exact name."""
        repo = MongoMenuItemRepository()
        await _insert_item(repo, name="Lazanja")
        found = await repo.get_by_name("Lazanja")
        assert found is not None
        assert found.name == "Lazanja"

    async def test_get_active_items_excludes_inactive(self) -> None:
        """get_active_items excludes soft-deleted items."""
        repo = MongoMenuItemRepository()
        await _insert_item(
            repo, item_number=1, name="Active Item", is_active=True
        )
        await _insert_item(
            repo, item_number=2, name="Inactive Item", is_active=False
        )
        items = await repo.get_active_items()
        assert len(items) == 1
        assert items[0].name == "Active Item"

    async def test_update(self) -> None:
        """Update modifies the specified fields."""
        repo = MongoMenuItemRepository()
        item = await _insert_item(repo)
        updated = await repo.update(item.id, {"price": 99.0})
        assert updated is not None
        assert updated.price == 99.0

    async def test_soft_delete_via_update(self) -> None:
        """Setting is_active=False hides item from active menu."""
        repo = MongoMenuItemRepository()
        item = await _insert_item(repo, is_active=True)
        await repo.update(item.id, {"is_active": False})
        active_items = await repo.get_active_items()
        assert len(active_items) == 0

    async def test_count(self) -> None:
        """Count returns correct number of documents."""
        repo = MongoMenuItemRepository()
        for i in range(3):
            await _insert_item(repo, item_number=i + 1, name=f"Item {i}")
        assert await repo.count({}) == 3
