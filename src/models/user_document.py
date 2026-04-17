"""User MongoDB document model."""

from beanie import Indexed
from pydantic import EmailStr

from src.enums import UserRole
from src.models.base_document import BaseDocument


class UserDocument(BaseDocument):
    """MongoDB document model for a Krusty Crab API user.

    Attributes:
        username (str): Unique username, indexed in MongoDB.
        email (EmailStr): Unique email address, indexed in MongoDB.
        hashed_password (str): Bcrypt-hashed password for authentication.
        role (UserRole): The user's permission level.
            Defaults to UserRole.GUEST.
        is_active (bool): Whether the user account is active.
            Defaults to True.
    """

    username: Indexed(str, unique=True)  # type: ignore
    email: Indexed(EmailStr, unique=True)  # type: ignore
    hashed_password: str
    role: UserRole = UserRole.GUEST
    is_active: bool = True

    class Settings:
        """Beanie document configuration."""

        name = "users"
