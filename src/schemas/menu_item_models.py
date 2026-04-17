"""Menu item request and response schemas."""

from abc import ABC
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from src.schemas.base_request import BaseRequest
from src.schemas.base_response import BaseResponse


class MenuItemBase(BaseModel, ABC):
    """Abstract base with shared menu item fields.

    Attributes:
        name (str): Display name of the menu item.
        price (float): Price of the menu item in shekels.
    """

    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)


class MenuItemCreate(MenuItemBase, BaseRequest):
    """Request schema for creating a new Krusty Crab menu item."""


class MenuItemResponse(MenuItemBase, BaseResponse):
    """Response schema for a Krusty Crab menu item.

    Attributes:
        item_number (int): The auto-assigned menu item identifier.
        is_active (bool): Whether the item is available for ordering.
        updated_at (datetime): When the menu item was last modified.
    """

    item_number: int
    is_active: bool
    updated_at: datetime


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
