"""Schema for admin user update requests."""

from typing import Optional

from pydantic import model_validator

from src.enums import UserRole
from src.schemas.base_request import BaseRequest


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
