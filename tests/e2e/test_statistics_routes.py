"""E2E tests for statistics and profits endpoints."""

from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestProfitsAccess:
    """Tests for /profits access control."""

    async def test_guest_cannot_access_profits(
        self, client: AsyncClient, auth_headers: Dict[str, str]
    ) -> None:
        """Guest cannot access profits (returns 403).

        Args:
            client (AsyncClient): The test HTTP client.
            auth_headers (Dict[str, str]): Guest authorization headers.
        """
        response = await client.get("/profits/", headers=auth_headers)
        assert response.status_code == 403

    async def test_worker_cannot_access_profits(
        self, client: AsyncClient, worker_headers: Dict[str, str]
    ) -> None:
        """Worker cannot access profits (returns 403).

        Args:
            client (AsyncClient): The test HTTP client.
            worker_headers (Dict[str, str]): Worker authorization headers.
        """
        response = await client.get("/profits/", headers=worker_headers)
        assert response.status_code == 403

    async def test_admin_can_access_profits(
        self, client: AsyncClient, admin_headers: Dict[str, str]
    ) -> None:
        """Admin can access profits.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
        """
        response = await client.get("/profits/", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["value"] == 0.0


@pytest.mark.asyncio
class TestStatisticsWithData:
    """Tests for statistics endpoints with seeded data."""

    async def test_total_profits_after_orders(
        self,
        client: AsyncClient,
        admin_headers: Dict[str, str],
        guest_headers: Dict[str, str],  # noqa: ARG002
        seed_order: Dict,  # noqa: ARG002
    ) -> None:
        """Total profits returns correct value after orders exist.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
            guest_headers (Dict[str, str]): Guest authorization headers.
            seed_order (Dict): A pre-created order (Schnitzel Alef at 66.0).
        """
        response = await client.get("/profits/", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["value"] == 66.0

    async def test_orders_by_status(
        self,
        client: AsyncClient,
        admin_headers: Dict[str, str],
        guest_headers: Dict[str, str],  # noqa: ARG002
        seed_order: Dict,  # noqa: ARG002
    ) -> None:
        """orders-by-status returns breakdown after orders exist.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
            guest_headers (Dict[str, str]): Guest authorization headers.
            seed_order (Dict): A pre-created order.
        """
        response = await client.get(
            "/statistics/orders-by-status", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        statuses = [item["status"] for item in data]
        assert "order_received" in statuses

    async def test_daily_average_profits(
        self,
        client: AsyncClient,
        admin_headers: Dict[str, str],
        guest_headers: Dict[str, str],  # noqa: ARG002
        seed_order: Dict,  # noqa: ARG002
    ) -> None:
        """Daily average returns total and average after orders exist.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
            guest_headers (Dict[str, str]): Guest authorization headers.
            seed_order (Dict): A pre-created order.
        """
        response = await client.get(
            "/profits/daily-average", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 66.0
        assert data["daily_average"] == 66.0
