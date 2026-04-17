"""Unit tests for MenuItemService."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from bson import ObjectId

from src.exceptions import DuplicateError, NotFoundError
from src.models.menu_item_document import MenuItemDocument
from src.schemas.menu_item.menu_item_create import MenuItemCreate
from src.schemas.menu_item.menu_item_update import MenuItemUpdate
from src.services.menu_item_service import MenuItemService


def _make_item(
    item_number: int = 1,
    name: str = "Schnitzel Alef",
    price: float = 66.0,
    is_active: bool = True,
) -> MenuItemDocument:
    """Build a MenuItemDocument for testing.

    Args:
        item_number (int): The menu item number.
        name (str): The item name.
        price (float): The item price.
        is_active (bool): Whether the item is active.

    Returns:
        MenuItemDocument: A test menu item document.
    """
    now = datetime.now(timezone.utc)
    return MenuItemDocument.model_construct(
        id=ObjectId(),
        item_number=item_number,
        name=name,
        price=price,
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
class TestCreateMenuItem:
    """Tests for MenuItemService.create_menu_item."""

    async def test_creates_when_name_unique(
        self,
        mock_menu_item_repo: AsyncMock,
        mock_menu_item_factory: AsyncMock,
    ) -> None:
        """Unique name results in successful creation.

        Args:
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
            mock_menu_item_factory (AsyncMock): Mocked menu item factory.
        """
        item = _make_item()
        mock_menu_item_repo.get_by_name.return_value = None
        mock_menu_item_factory.create.return_value = item
        mock_menu_item_repo.create.return_value = item
        service = MenuItemService(mock_menu_item_repo, mock_menu_item_factory)
        data = MenuItemCreate(name="Schnitzel Alef", price=66.0)
        result = await service.create_menu_item(data)
        assert result.name == "Schnitzel Alef"

    async def test_raises_duplicate_on_existing_name(
        self,
        mock_menu_item_repo: AsyncMock,
        mock_menu_item_factory: AsyncMock,
    ) -> None:
        """Existing name raises DuplicateError.

        Args:
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
            mock_menu_item_factory (AsyncMock): Mocked menu item factory.
        """
        mock_menu_item_repo.get_by_name.return_value = _make_item()
        service = MenuItemService(mock_menu_item_repo, mock_menu_item_factory)
        data = MenuItemCreate(name="Schnitzel Alef", price=66.0)
        with pytest.raises(DuplicateError):
            await service.create_menu_item(data)


@pytest.mark.asyncio
class TestGetMenuItem:
    """Tests for MenuItemService.get_menu_item."""

    async def test_returns_item_when_found(
        self,
        mock_menu_item_repo: AsyncMock,
        mock_menu_item_factory: AsyncMock,
    ) -> None:
        """Found item is returned.

        Args:
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
            mock_menu_item_factory (AsyncMock): Mocked menu item factory.
        """
        item = _make_item()
        mock_menu_item_repo.get_by_item_number.return_value = item
        service = MenuItemService(mock_menu_item_repo, mock_menu_item_factory)
        result = await service.get_menu_item(1)
        assert result.item_number == 1

    async def test_raises_not_found(
        self,
        mock_menu_item_repo: AsyncMock,
        mock_menu_item_factory: AsyncMock,
    ) -> None:
        """Missing item raises NotFoundError.

        Args:
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
            mock_menu_item_factory (AsyncMock): Mocked menu item factory.
        """
        mock_menu_item_repo.get_by_item_number.return_value = None
        service = MenuItemService(mock_menu_item_repo, mock_menu_item_factory)
        with pytest.raises(NotFoundError):
            await service.get_menu_item(999)


@pytest.mark.asyncio
class TestUpdateMenuItem:
    """Tests for MenuItemService.update_menu_item."""

    async def test_raises_duplicate_if_name_taken_by_other(
        self,
        mock_menu_item_repo: AsyncMock,
        mock_menu_item_factory: AsyncMock,
    ) -> None:
        """Name already used by another item raises DuplicateError.

        Args:
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
            mock_menu_item_factory (AsyncMock): Mocked menu item factory.
        """
        item = _make_item(item_number=1, name="Schnitzel Alef")
        other_item = _make_item(item_number=2, name="Lazanja")
        mock_menu_item_repo.get_by_item_number.return_value = item
        mock_menu_item_repo.get_by_name.return_value = other_item
        service = MenuItemService(mock_menu_item_repo, mock_menu_item_factory)
        data = MenuItemUpdate(name="Lazanja")
        with pytest.raises(DuplicateError):
            await service.update_menu_item(1, data)


@pytest.mark.asyncio
class TestDeleteMenuItem:
    """Tests for MenuItemService.delete_menu_item."""

    async def test_soft_deletes_active_item(
        self,
        mock_menu_item_repo: AsyncMock,
        mock_menu_item_factory: AsyncMock,
    ) -> None:
        """Deleting an active item calls update with is_active=False.

        Args:
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
            mock_menu_item_factory (AsyncMock): Mocked menu item factory.
        """
        item = _make_item(is_active=True)
        mock_menu_item_repo.get_by_item_number.return_value = item
        service = MenuItemService(mock_menu_item_repo, mock_menu_item_factory)
        await service.delete_menu_item(1)
        call_kwargs = mock_menu_item_repo.update.call_args
        update_data = call_kwargs[0][1]
        assert update_data.get("is_active") is False
