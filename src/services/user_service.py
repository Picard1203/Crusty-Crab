"""Business logic for administrator user management operations."""

import logging
from typing import Any, Dict

from src.exceptions import NotFoundException
from src.models import UserDocument
from src.repositories import UserRepository
from src.schemas import PaginatedResponse, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Orchestrates admin user management business logic.

    Attributes:
        _repository (UserRepository): User data access.
    """

    def __init__(self, repository: UserRepository) -> None:
        """Initialize with repository dependency.

        Args:
            repository (UserRepository): The user repository interface.
        """
        self._repository: UserRepository = repository

    async def get_user(self, username: str) -> UserDocument:
        """Retrieve a single user by username.

        Args:
            username (str): The username to look up.

        Returns:
            UserDocument: The found user document.

        Raises:
            NotFoundException: If no user exists with this username.
        """
        logger.info(f"Fetching user '{username}'")
        user = await self._repository.get_by_username(username)
        if user is None:
            raise NotFoundException(f"User '{username}' not found")
        return user

    async def get_all_users(
        self, skip: int, limit: int
    ) -> PaginatedResponse[UserDocument]:
        """Retrieve a paginated list of all users.

        Args:
            skip (int): Number of documents to skip.
            limit (int): Maximum number of documents to return.

        Returns:
            PaginatedResponse[UserDocument]: Paginated results with metadata.
        """
        logger.info(f"Listing users skip={skip} limit={limit}")
        users = await self._repository.get_all(skip, limit, {})
        total = await self._repository.count({})
        return PaginatedResponse(
            items=users,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total,
        )

    async def update_user(
        self, username: str, data: UserUpdate
    ) -> UserDocument:
        """Update a user's role or active status.

        Args:
            username (str): The username of the user to update.
            data (UserUpdate): The validated update request.

        Returns:
            UserDocument: The updated user document.

        Raises:
            NotFoundException: If no user exists with this username.
        """
        logger.info(f"Updating user '{username}'")
        user = await self._get_existing_user(username)
        update_data: Dict[str, Any] = data.model_dump(exclude_none=True)
        return await self._apply_update(user.id, update_data)

    async def delete_user(self, username: str) -> None:
        """Permanently delete a user.

        Args:
            username (str): The username of the user to delete.

        Raises:
            NotFoundException: If no user exists with this username.
        """
        logger.info(f"Deleting user '{username}'")
        user = await self._get_existing_user(username)
        await self._repository.delete(user.id)

    async def _get_existing_user(self, username: str) -> UserDocument:
        """Fetch a user by username or raise if not found.

        Args:
            username (str): The username to look up.

        Returns:
            UserDocument: The found user document.

        Raises:
            NotFoundException: If no user exists with the given username.
        """
        user = await self._repository.get_by_username(username)
        if user is None:
            raise NotFoundException(f"User '{username}' not found")
        return user

    async def _apply_update(
        self, internal_id: Any, update_data: Dict[str, Any]
    ) -> UserDocument:
        """Commit the update to the repository.

        Args:
            internal_id (Any): The internal database ID.
            update_data (Dict[str, Any]): The fields and values to update.

        Returns:
            UserDocument: The updated user document.

        Raises:
            NotFoundException: If the update fails because the record was
                not found.
        """
        updated = await self._repository.update(internal_id, update_data)
        if updated is None:
            raise NotFoundException("User record missing during update")
        return updated
