"""Integration test fixtures — real MongoDB connection and cleanup."""

from typing import AsyncGenerator

import pytest_asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.models import (
    CounterDocument,
    MenuItemDocument,
    OrderDocument,
    UserDocument,
)
from src.settings import get_settings


@pytest_asyncio.fixture(autouse=True)
async def setup_database(
    motor_client: AsyncIOMotorClient,
) -> AsyncGenerator[None, None]:
    """Initialize Beanie and clean all collections before each test.

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
