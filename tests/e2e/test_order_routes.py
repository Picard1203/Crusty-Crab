"""E2E tests for order endpoints."""

from typing import Dict

import pytest
from httpx import AsyncClient

from src.auth.token_handler import TokenHandler
from src.settings import get_settings


@pytest.mark.asyncio
class TestCreateOrder:
    """Tests for POST /orders/."""

    async def test_creates_order_successfully(
        self,
        client: AsyncClient,
        guest_headers: Dict[str, str],
        seed_menu: None,  # noqa: ARG002
    ) -> None:
        """Authenticated user can create an order.

        Args:
            client (AsyncClient): The test HTTP client.
            guest_headers (Dict[str, str]): Guest authorization headers.
            seed_menu (None): Ensures menu items exist.
        """
        response = await client.post(
            "/orders/",
            json={"orderer_name": "guestuser", "items": ["Schnitzel Alef"]},
            headers=guest_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["order_number"] >= 1
        assert data["total_price"] == 66.0

    async def test_unauthenticated_returns_401(
        self, client: AsyncClient, seed_menu: None  # noqa: ARG002
    ) -> None:
        """Unauthenticated order creation returns 401."""
        response = await client.post(
            "/orders/",
            json={"orderer_name": "nobody", "items": ["Schnitzel Alef"]},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetOrder:
    """Tests for GET /orders/{order_number}."""

    async def test_guest_can_get_own_order(
        self,
        client: AsyncClient,
        guest_headers: Dict[str, str],
        seed_order: Dict,
    ) -> None:
        """Guest can retrieve their own order.

        Args:
            client (AsyncClient): The test HTTP client.
            guest_headers (Dict[str, str]): Guest authorization headers.
            seed_order (Dict): A pre-created order for guestuser.
        """
        number = seed_order["order_number"]
        response = await client.get(f"/orders/{number}", headers=guest_headers)
        assert response.status_code == 200
        assert response.json()["order_number"] == number

    async def test_guest_cannot_get_others_order(
        self,
        client: AsyncClient,
        worker_headers: Dict[str, str],  # noqa: ARG002
        guest_headers: Dict[str, str],  # noqa: ARG002
        seed_order: Dict,
    ) -> None:
        """Guest cannot retrieve another user's order (returns 403).

        Args:
            client (AsyncClient): The test HTTP client.
            worker_headers (Dict[str, str]): Worker authorization headers.
            guest_headers (Dict[str, str]): Guest authorization headers
                (triggers seed_order fixture setup).
            seed_order (Dict): An order owned by guestuser.
        """
        await client.post(
            "/auth/register",
            json={
                "username": "otherguest",
                "email": "other@example.com",
                "password": "testpass123",
                "role": "guest",
            },
        )
        other_token = TokenHandler(get_settings()).create_access_token(
            {"sub": "otherguest"}
        )
        other_headers = {"Authorization": f"Bearer {other_token}"}
        number = seed_order["order_number"]
        response = await client.get(
            f"/orders/{number}", headers=other_headers
        )
        assert response.status_code == 403

    async def test_worker_can_get_any_order(
        self,
        client: AsyncClient,
        worker_headers: Dict[str, str],
        guest_headers: Dict[str, str],  # noqa: ARG002
        seed_order: Dict,
    ) -> None:
        """Worker can retrieve any user's order.

        Args:
            client (AsyncClient): The test HTTP client.
            worker_headers (Dict[str, str]): Worker authorization headers.
            guest_headers (Dict[str, str]): Guest authorization headers
                (triggers seed_order fixture setup).
            seed_order (Dict): An order owned by guestuser.
        """
        number = seed_order["order_number"]
        response = await client.get(
            f"/orders/{number}", headers=worker_headers
        )
        assert response.status_code == 200


@pytest.mark.asyncio
class TestUpdateOrderStatus:
    """Tests for PATCH /orders/{order_number}/status."""

    async def test_worker_can_advance_status(
        self,
        client: AsyncClient,
        worker_headers: Dict[str, str],
        guest_headers: Dict[str, str],  # noqa: ARG002
        seed_order: Dict,
    ) -> None:
        """Worker can advance order from received to confirmed.

        Args:
            client (AsyncClient): The test HTTP client.
            worker_headers (Dict[str, str]): Worker authorization headers.
            guest_headers (Dict[str, str]): Guest authorization headers.
            seed_order (Dict): A pre-created order.
        """
        number = seed_order["order_number"]
        response = await client.patch(
            f"/orders/{number}/status",
            json={"status": "order_confirmed"},
            headers=worker_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "order_confirmed"

    async def test_guest_cannot_update_status(
        self,
        client: AsyncClient,
        guest_headers: Dict[str, str],
        seed_order: Dict,
    ) -> None:
        """Guest cannot update order status (returns 403).

        Args:
            client (AsyncClient): The test HTTP client.
            guest_headers (Dict[str, str]): Guest authorization headers.
            seed_order (Dict): A pre-created order.
        """
        number = seed_order["order_number"]
        response = await client.patch(
            f"/orders/{number}/status",
            json={"status": "order_confirmed"},
            headers=guest_headers,
        )
        assert response.status_code == 403

    async def test_invalid_transition_returns_422(
        self,
        client: AsyncClient,
        worker_headers: Dict[str, str],
        guest_headers: Dict[str, str],  # noqa: ARG002
        seed_order: Dict,
    ) -> None:
        """Invalid status transition returns 422.

        Args:
            client (AsyncClient): The test HTTP client.
            worker_headers (Dict[str, str]): Worker authorization headers.
            guest_headers (Dict[str, str]): Guest headers.
            seed_order (Dict): A pre-created order in order_received status.
        """
        number = seed_order["order_number"]
        response = await client.patch(
            f"/orders/{number}/status",
            json={"status": "order_complete"},
            headers=worker_headers,
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestDeleteOrder:
    """Tests for DELETE /orders/{order_number}."""

    async def test_guest_can_delete_own_order(
        self,
        client: AsyncClient,
        guest_headers: Dict[str, str],
        seed_order: Dict,
    ) -> None:
        """Guest can delete their own order.

        Args:
            client (AsyncClient): The test HTTP client.
            guest_headers (Dict[str, str]): Guest authorization headers.
            seed_order (Dict): A pre-created order.
        """
        number = seed_order["order_number"]
        response = await client.delete(
            f"/orders/{number}", headers=guest_headers
        )
        assert response.status_code == 204
