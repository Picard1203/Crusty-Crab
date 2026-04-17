"""E2E tests for auth endpoints."""

from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthRegister:
    """Tests for POST /auth/register."""

    async def test_register_creates_user(self, client: AsyncClient) -> None:
        """Valid registration returns 201 with user data."""
        response = await client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepassword",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] == "guest"
        assert data["is_active"] is True

    async def test_duplicate_username_returns_409(
        self, client: AsyncClient
    ) -> None:
        """Duplicate username returns 409."""
        payload = {
            "username": "dupeuser",
            "email": "dupe@example.com",
            "password": "testpass123",
        }
        await client.post("/auth/register", json=payload)
        payload["email"] = "other@example.com"
        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 409

    async def test_duplicate_email_returns_409(
        self, client: AsyncClient
    ) -> None:
        """Duplicate email returns 409."""
        await client.post(
            "/auth/register",
            json={
                "username": "user1",
                "email": "shared@example.com",
                "password": "testpass123",
            },
        )
        response = await client.post(
            "/auth/register",
            json={
                "username": "user2",
                "email": "shared@example.com",
                "password": "testpass123",
            },
        )
        assert response.status_code == 409


@pytest.mark.asyncio
class TestAuthMe:
    """Tests for GET /auth/me."""

    async def test_me_returns_current_user(
        self, client: AsyncClient, auth_headers: Dict[str, str]
    ) -> None:
        """Authenticated GET /auth/me returns current user.

        Args:
            client (AsyncClient): The test HTTP client.
            auth_headers (Dict[str, str]): Authorization headers.
        """
        response = await client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["username"] == "guestuser"

    async def test_me_unauthenticated_returns_401(
        self, client: AsyncClient
    ) -> None:
        """Unauthenticated GET /auth/me returns 401."""
        response = await client.get("/auth/me")
        assert response.status_code == 401
