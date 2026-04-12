"""Schema for user response payloads."""

from pydantic import EmailStr

from src.enums import UserRole
from src.schemas.base_response import BaseResponse


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
