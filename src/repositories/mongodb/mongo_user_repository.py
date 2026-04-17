"""Concrete MongoDB implementation of the user repository."""

import logging
from typing import Any, Dict, List, Optional

from bson import ObjectId

from src.models import UserDocument
from src.repositories import UserRepository

logger = logging.getLogger(__name__)


class MongoUserRepository(UserRepository):
    """Beanie-based implementation of UserRepository."""

    async def get_by_id(self, entity_id: ObjectId) -> Optional[UserDocument]:
        """Retrieve a user by MongoDB ObjectId.

        Args:
            entity_id (ObjectId): The MongoDB document ID.

        Returns:
            Optional[UserDocument]: The user if found, None otherwise.
        """
        logger.debug(f"Fetching user by ObjectId {entity_id}")
        return await UserDocument.get(entity_id)

    async def get_by_username(self, username: str) -> Optional[UserDocument]:
        """Retrieve a user by their unique username.

        Args:
            username (str): The username to search for.

        Returns:
            Optional[UserDocument]: The user if found, None otherwise.
        """
        logger.debug(f"Fetching user by username '{username}'")
        return await UserDocument.find_one(UserDocument.username == username)

    async def get_by_email(self, email: str) -> Optional[UserDocument]:
        """Retrieve a user by their unique email address.

        Args:
            email (str): The email address to search for.

        Returns:
            Optional[UserDocument]: The user if found, None otherwise.
        """
        logger.debug(f"Fetching user by email '{email}'")
        return await UserDocument.find_one(UserDocument.email == email)

    async def get_all(
        self, skip: int, limit: int, filters: Dict[str, Any]
    ) -> List[UserDocument]:
        """Retrieve users with pagination and filtering.

        Args:
            skip (int): Number of documents to skip.
            limit (int): Maximum number of documents to return.
            filters (Dict[str, Any]): Key-value pairs for query filtering.

        Returns:
            List[UserDocument]: The matching users.
        """
        query = self._build_query(filters)
        logger.debug(
            f"Querying users with filters {filters}, skip={skip}, limit={limit}"
        )
        return await UserDocument.find(query).skip(skip).limit(limit).to_list()

    async def create(self, entity: UserDocument) -> UserDocument:
        """Persist a new user document to MongoDB.

        Args:
            entity (UserDocument): The document to insert.

        Returns:
            UserDocument: The inserted document with _id populated.
        """
        logger.info(f"Creating user '{entity.username}'")
        await entity.insert()
        return entity

    async def update(
        self, entity_id: ObjectId, data: Dict[str, Any]
    ) -> Optional[UserDocument]:
        """Update an existing user by ObjectId.

        Args:
            entity_id (ObjectId): The MongoDB document ID.
            data (Dict[str, Any]): Fields to update with their new values.

        Returns:
            Optional[UserDocument]: The updated user, None if not found.
        """
        logger.info(
            f"Updating user {entity_id} with fields {list(data.keys())}"
        )
        user = await UserDocument.get(entity_id)
        if user is None:
            return None
        await user.set(data)
        return user

    async def delete(self, entity_id: ObjectId) -> bool:
        """Delete a user by ObjectId.

        Args:
            entity_id (ObjectId): The MongoDB document ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        logger.info(f"Deleting user {entity_id}")
        user = await UserDocument.get(entity_id)
        if user is None:
            return False
        await user.delete()
        return True

    async def count(self, filters: Dict[str, Any]) -> int:
        """Count users matching the given filters.

        Args:
            filters (Dict[str, Any]): Key-value pairs for query filtering.

        Returns:
            int: Number of matching users.
        """
        query = self._build_query(filters)
        return await UserDocument.find(query).count()

    @staticmethod
    def _build_query(filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build a MongoDB query dict from filter parameters.

        Args:
            filters (Dict[str, Any]): Raw filter key-value pairs.

        Returns:
            Dict[str, Any]: MongoDB-compatible query dictionary.
        """
        query: Dict[str, Any] = {}
        if filters.get("is_active") is not None:
            query["is_active"] = filters["is_active"]
        if filters.get("role") is not None:
            query["role"] = filters["role"]
        return query
