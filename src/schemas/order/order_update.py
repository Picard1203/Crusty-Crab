"""Schema for order update requests."""

from typing import List, Optional

from pydantic import Field, model_validator

from src.schemas.base_request import BaseRequest


class OrderUpdate(BaseRequest):
    """Request schema for updating an existing order.

    Attributes:
        orderer_name (Optional[str]): Updated orderer name.
        items (Optional[List[str]]): Updated list of menu item names.
    """

    orderer_name: Optional[str] = Field(
        default=None, min_length=1, max_length=100
    )
    items: Optional[List[str]] = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "OrderUpdate":
        """Ensure at least one field is provided for the update.

        Returns:
            OrderUpdate: The validated update schema.

        Raises:
            ValueError: If all fields are None.
        """
        if self.orderer_name is None and self.items is None:
            raise ValueError("At least one field must be provided for update")
        return self
