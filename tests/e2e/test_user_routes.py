"""E2E tests for admin user management endpoints."""

from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUserManagementAccess:
    """Tests for /users access control."""

    async def test_guest_cannot_list_users(
        self, client: AsyncClient, auth_headers: Dict[str, str]
    ) -> None:
        """Guest cannot access user list (returns 403).

        Args:
            client (AsyncClient): The test HTTP client.
            auth_headers (Dict[str, str]): Guest authorization headers.
        """
        response = await client.get("/users/", headers=auth_headers)
        assert response.status_code == 403

    async def test_worker_cannot_list_users(
        self, client: AsyncClient, worker_headers: Dict[str, str]
    ) -> None:
        """Worker cannot access user list (returns 403).

        Args:
            client (AsyncClient): The test HTTP client.
            worker_headers (Dict[str, str]): Worker authorization headers.
        """
        response = await client.get("/users/", headers=worker_headers)
        assert response.status_code == 403

    async def test_admin_can_list_users(
        self,
        client: AsyncClient,
        admin_headers: Dict[str, str],
        auth_headers: Dict[str, str],  # noqa: ARG002
    ) -> None:
        """Admin can list all users.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
            auth_headers (Dict[str, str]): Creates guest fixture user.
        """
        response = await client.get("/users/", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1


@pytest.mark.asyncio
class TestUserCRUD:
    """Tests for admin user CRUD operations."""

    async def test_admin_can_get_user(
        self, client: AsyncClient, admin_headers: Dict[str, str]
    ) -> None:
        """Admin can retrieve a specific user by username.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
        """
        await client.post(
            "/auth/register",
            json={
                "username": "targetuser",
                "email": "target@example.com",
                "password": "testpass123",
            },
        )
        response = await client.get(
            "/users/targetuser", headers=admin_headers
        )
        assert response.status_code == 200
        assert response.json()["username"] == "targetuser"

    async def test_admin_can_update_user_role(
        self, client: AsyncClient, admin_headers: Dict[str, str]
    ) -> None:
        """Admin can update a user's role.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
        """
        await client.post(
            "/auth/register",
            json={
                "username": "upgradeuser",
                "email": "upgrade@example.com",
                "password": "testpass123",
            },
        )
        response = await client.put(
            "/users/upgradeuser",
            json={"role": "worker"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["role"] == "worker"

    async def test_admin_can_delete_user(
        self, client: AsyncClient, admin_headers: Dict[str, str]
    ) -> None:
        """Admin can delete a user.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
        """
        await client.post(
            "/auth/register",
            json={
                "username": "deleteuser",
                "email": "delete@example.com",
                "password": "testpass123",
            },
        )
        response = await client.delete(
            "/users/deleteuser", headers=admin_headers
        )
        assert response.status_code == 204

    async def test_get_nonexistent_user_returns_404(
        self, client: AsyncClient, admin_headers: Dict[str, str]
    ) -> None:
        """Getting a nonexistent user returns 404.

        Args:
            client (AsyncClient): The test HTTP client.
            admin_headers (Dict[str, str]): Admin authorization headers.
        """
        response = await client.get(
            "/users/doesnotexist", headers=admin_headers
        )
        assert response.status_code == 404
