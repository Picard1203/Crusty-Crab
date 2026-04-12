"""MongoDB database connection implementation."""

import logging
from typing import Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.database import Database
from src.models import (
    CounterDocument,
    MenuItemDocument,
    OrderDocument,
    UserDocument,
)
from src.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class MongoDatabase(Database):
    """Concrete MongoDB implementation of the Database interface.

    Attributes:
        _settings (Settings): Application settings for database configuration.
        _client (AsyncIOMotorClient): The Motor client for MongoDB operations.
    """

    def __init__(self) -> None:
        """Initialize the MongoDatabase with application settings."""
        self._settings: Settings = get_settings()
        self._client: Optional[AsyncIOMotorClient] = None

    async def connect(self) -> None:
        """Establish a connection to the MongoDB server."""
        logger.info(f"Connecting to mongo at {self._settings.mongodb_url}")
        self._client = AsyncIOMotorClient(self._settings.mongodb_url)
        logger.info("MongoDB connection established")

    async def disconnect(self) -> None:
        """Close the MongoDB connection if it exists."""
        if self._client is not None:
            self._client.close()
            logger.info("MongoDB connection closed")

    async def init_models(self) -> None:
        """Initialize Beanie with the MongoDB database and document models."""
        database = self._client[self._settings.database_name]
        await init_beanie(
            database=database,
            document_models=[
                OrderDocument,
                MenuItemDocument,
                UserDocument,
                CounterDocument,
            ],
        )
        logger.info("Beanie models initialized")

    async def get_session(self):
        """Start a new MongoDB client session.

        Returns:
            AsyncIOMotorClientSession: A new Motor session for transactions.
        """
        return await self._client.start_session()
