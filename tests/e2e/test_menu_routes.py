"""E2E tests for menu item endpoints."""

from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestPublicMenu:
    """Tests for public GET /menu endpoints."""

    async def test_get_active_menu_is_public(
        self, client: AsyncClient, seed_menu: None  # noqa: ARG002
    ) -> None:
        """GET /menu/ is accessible without authentication."""
        response = await client.get("/menu/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_menu_item_by_number(
        self,
        client: AsyncClient,
        admin_headers: Dict[str, str],  # noqa: ARG002
        seed_menu: None,  # noqa: ARG002
    ) -> None:
        """GET /menu/{number} returns a specific menu item.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
            seed_menu (None): Ensures menu items exist.
        """
        menu = await client.get("/menu/")
        item_number = menu.json()[0]["item_number"]
        response = await client.get(f"/menu/{item_number}")
        assert response.status_code == 200
        assert response.json()["item_number"] == item_number


@pytest.mark.asyncio
class TestAdminMenuCRUD:
    """Tests for admin-only menu management."""

    async def test_create_menu_item(
        self, client: AsyncClient, admin_headers: Dict[str, str]
    ) -> None:
        """Admin can create a menu item.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
        """
        response = await client.post(
            "/menu/",
            json={"name": "New Dish", "price": 35.0},
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Dish"
        assert data["is_active"] is True

    async def test_guest_cannot_create_menu_item(
        self, client: AsyncClient, auth_headers: Dict[str, str]
    ) -> None:
        """Guest creating a menu item returns 403.

        Args:
            client (AsyncClient): The test HTTP client.
            auth_headers (Dict[str, str]): Guest authorization headers.
        """
        response = await client.post(
            "/menu/",
            json={"name": "Forbidden Dish", "price": 20.0},
            headers=auth_headers,
        )
        assert response.status_code == 403

    async def test_soft_delete_returns_204(
        self,
        client: AsyncClient,
        admin_headers: Dict[str, str],
        seed_menu: None,  # noqa: ARG002
    ) -> None:
        """Admin soft-deleting a menu item returns 204.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
            seed_menu (None): Ensures menu items exist.
        """
        menu = await client.get("/menu/")
        item_number = menu.json()[0]["item_number"]
        response = await client.delete(
            f"/menu/{item_number}", headers=admin_headers
        )
        assert response.status_code == 204

    async def test_duplicate_name_returns_409(
        self, client: AsyncClient, admin_headers: Dict[str, str]
    ) -> None:
        """Duplicate menu item name returns 409.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
        """
        await client.post(
            "/menu/",
            json={"name": "Unique Dish", "price": 30.0},
            headers=admin_headers,
        )
        response = await client.post(
            "/menu/",
            json={"name": "Unique Dish", "price": 25.0},
            headers=admin_headers,
        )
        assert response.status_code == 409
