"""Schema for user registration requests."""

from pydantic import EmailStr, Field, field_validator

from src.enums import UserRole
from src.schemas.base_request import BaseRequest


class UserCreate(BaseRequest):
    """Request schema for registering a new Krusty Crab API user.

    Attributes:
        username (str): Unique username (3-30 chars, alphanumeric + underscores).
        email (EmailStr): Unique email address.
        password (str): Plaintext password (min 8 chars, hashed before storage).
        role (UserRole): User permission level. Defaults to GUEST.
    """

    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.GUEST

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        """Ensure username contains only alphanumeric characters and underscores.

        Args:
            value (str): The raw username.

        Returns:
            str: The validated username.

        Raises:
            ValueError: If username contains invalid characters.
        """
        if value.replace("_", "").isalnum() is False:
            raise ValueError(
                "Username must contain only alphanumeric characters "
                "and underscores"
            )
        return value
