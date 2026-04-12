"""Schema for menu item update requests."""

from typing import Optional

from pydantic import Field, model_validator

from src.schemas.base_request import BaseRequest


class MenuItemUpdate(BaseRequest):
    """Request schema for updating an existing menu item.

    Attributes:
        name (Optional[str]): Updated display name.
        price (Optional[float]): Updated price in shekels.
    """

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    price: Optional[float] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "MenuItemUpdate":
        """Ensure at least one field is provided for the update.

        Returns:
            MenuItemUpdate: The validated update schema.

        Raises:
            ValueError: If all fields are None.
        """
        if self.name is None and self.price is None:
            raise ValueError("At least one field must be provided for update")
        return self
