"""Abstract user repository with domain-specific query methods."""

from abc import abstractmethod
from typing import Optional

from src.models.user_document import UserDocument
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Extends BaseRepository with user-specific access patterns."""

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[UserDocument]:
        """Retrieve a user by their unique username.

        Args:
            username (str): The username to search for.

        Returns:
            Optional[UserDocument]: The user if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserDocument]:
        """Retrieve a user by their unique email address.

        Args:
            email (str): The email address to search for.

        Returns:
            Optional[UserDocument]: The user if found, None otherwise.
        """
        raise NotImplementedError
