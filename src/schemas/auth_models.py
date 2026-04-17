"""Authentication and user request/response schemas."""

from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from src.enums import UserRole
from src.schemas.base_request import BaseRequest
from src.schemas.base_response import BaseResponse


class TokenRefreshRequest(BaseRequest):
    """Request schema for exchanging a refresh token.

    Attributes:
        refresh_token (str): The valid refresh JWT to exchange.
    """

    refresh_token: str


class TokenResponse(BaseModel):
    """Response schema for authentication tokens.

    Attributes:
        access_token (str): Short-lived JWT for API authorization.
        refresh_token (str): Long-lived JWT for obtaining new access tokens.
        token_type (str): Always 'bearer'.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


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


class UserResponse(BaseResponse):
    """Response schema for a Krusty Crab API user.

    Attributes:
        username (str): The user's unique username.
        email (EmailStr): The user's email address.
        role (UserRole): The user's permission level.
        is_active (bool): Whether the account is active.
    """

    username: str
    email: EmailStr
    role: UserRole
    is_active: bool


class UserUpdate(BaseRequest):
    """Request schema for updating a user's role or active status.

    Only administrators can use this endpoint.
    At least one field must be provided per update.

    Attributes:
        role (Optional[UserRole]): Updated permission level.
        is_active (Optional[bool]): Updated activation status.
    """

    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "UserUpdate":
        """Ensure at least one field is provided for the update.

        Returns:
            UserUpdate: The validated update schema.

        Raises:
            ValueError: If all fields are None.
        """
        if self.role is None and self.is_active is None:
            raise ValueError("At least one field must be provided for update")
        return self
