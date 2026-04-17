"""Root test configuration — environment setup and session-scoped fixtures."""

import os

os.environ["DATABASE_NAME"] = "krusty_crab_test"
os.environ["JWT_SECRET"] = "test-secret-key-not-for-production"

import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from src.settings import get_settings

get_settings.cache_clear()


@pytest_asyncio.fixture
async def motor_client():
    """Create a session-scoped Motor client shared across all tests.

    Yields:
        AsyncIOMotorClient: The MongoDB client.
    """
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    yield client
    client.close()
