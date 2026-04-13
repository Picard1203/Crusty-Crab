"""E2E test fixtures — app client, auth, and seed data."""

from typing import AsyncGenerator, Dict

import pytest_asyncio
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from src.app import create_app
from src.auth.token_handler import TokenHandler
from src.database.mongodb.mongo_database import MongoDatabase
from src.models import (
    CounterDocument,
    MenuItemDocument,
    OrderDocument,
    UserDocument,
)
from src.settings import get_settings


@pytest_asyncio.fixture(autouse=True)
async def clean_database(
    motor_client: AsyncIOMotorClient,
) -> AsyncGenerator[None, None]:
    """Drop all collections before each E2E test for isolation.

    Args:
        motor_client (AsyncIOMotorClient): The session-scoped Motor client.

    Yields:
        None: Control to the test function.
    """
    settings = get_settings()
    database = motor_client[settings.database_name]
    for collection_name in await database.list_collection_names():
        await database[collection_name].drop()
    await init_beanie(
        database=database,
        document_models=[
            OrderDocument,
            MenuItemDocument,
            UserDocument,
            CounterDocument,
        ],
    )
    yield


@pytest_asyncio.fixture
async def client(
    motor_client: AsyncIOMotorClient,
) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP test client wrapping the FastAPI app.

    Bypasses the lifespan to avoid menu seeding and full DB connect.
    Attaches the test Motor client directly to app state.

    Args:
        motor_client (AsyncIOMotorClient): The test Motor client.

    Yields:
        AsyncClient: The test HTTP client.
    """
    app = create_app()
    database = MongoDatabase()
    database._client = motor_client
    app.state.database = database
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _make_token(username: str) -> str:
    """Create a JWT access token for a given username.

    Args:
        username (str): The username to embed in the token.

    Returns:
        str: The signed JWT access token.
    """
    return TokenHandler(get_settings()).create_access_token({"sub": username})


@pytest_asyncio.fixture
async def guest_headers(client: AsyncClient) -> Dict[str, str]:
    """Register a guest user and return valid auth headers.

    Args:
        client (AsyncClient): The test HTTP client.

    Returns:
        Dict[str, str]: Authorization header with bearer token.
    """
    await client.post(
        "/auth/register",
        json={
            "username": "guestuser",
            "email": "guest@example.com",
            "password": "testpassword123",
            "role": "guest",
        },
    )
    return {"Authorization": f"Bearer {_make_token('guestuser')}"}


@pytest_asyncio.fixture
async def auth_headers(guest_headers: Dict[str, str]) -> Dict[str, str]:
    """Alias for guest_headers for backward compat with shared tests.

    Args:
        guest_headers (Dict[str, str]): Guest authorization headers.

    Returns:
        Dict[str, str]: Authorization header with bearer token.
    """
    return guest_headers


@pytest_asyncio.fixture
async def worker_headers(client: AsyncClient) -> Dict[str, str]:
    """Register a worker user and return valid auth headers.

    Args:
        client (AsyncClient): The test HTTP client.

    Returns:
        Dict[str, str]: Authorization header with bearer token.
    """
    await client.post(
        "/auth/register",
        json={
            "username": "workeruser",
            "email": "worker@example.com",
            "password": "testpassword123",
            "role": "worker",
        },
    )
    return {"Authorization": f"Bearer {_make_token('workeruser')}"}


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient) -> Dict[str, str]:
    """Register an administrator user and return valid auth headers.

    Args:
        client (AsyncClient): The test HTTP client.

    Returns:
        Dict[str, str]: Authorization header with bearer token.
    """
    await client.post(
        "/auth/register",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "testpassword123",
            "role": "administrator",
        },
    )
    return {"Authorization": f"Bearer {_make_token('adminuser')}"}


@pytest_asyncio.fixture
async def seed_menu(client: AsyncClient, admin_headers: Dict[str, str]) -> None:
    """Seed default menu items for tests that need an active menu.

    Args:
        client (AsyncClient): The test HTTP client.
        admin_headers (Dict[str, str]): Administrator authorization headers.
    """
    items = [
        {"name": "Schnitzel Alef", "price": 66.0},
        {"name": "Lazanja", "price": 42.0},
        {"name": "Arais", "price": 24.0},
    ]
    for item in items:
        await client.post("/menu/", json=item, headers=admin_headers)


@pytest_asyncio.fixture
async def seed_order(
    client: AsyncClient,
    guest_headers: Dict[str, str],
    seed_menu: None,  # noqa: ARG001
) -> Dict:
    """Create and return a seed order for the guest user.

    Args:
        client (AsyncClient): The test HTTP client.
        guest_headers (Dict[str, str]): Guest authorization headers.
        seed_menu (None): Ensures menu items exist.

    Returns:
        Dict: The created order response data.
    """
    response = await client.post(
        "/orders/",
        json={"orderer_name": "guestuser", "items": ["Schnitzel Alef"]},
        headers=guest_headers,
    )
    return response.json()
