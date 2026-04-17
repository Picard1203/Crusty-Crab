"""Order request and response schemas."""

from abc import ABC
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from src.enums import OrderStatus
from src.schemas.base_request import BaseRequest
from src.schemas.base_response import BaseResponse


class OrderBase(BaseModel, ABC):
    """Abstract base with shared order fields.

    Attributes:
        orderer_name (str): The name of the customer placing the order.
        items (List[str]): Names of menu items being ordered.
    """

    orderer_name: str = Field(min_length=1, max_length=100)
    items: List[str] = Field(min_length=1)

    @field_validator("orderer_name", mode="before")
    @classmethod
    def strip_whitespace(cls, value: object) -> object:
        """Strip leading/trailing whitespace from orderer name.

        Args:
            value (object): The raw input value.

        Returns:
            object: Trimmed string if input was a string, otherwise unchanged.
        """
        if isinstance(value, str) is True:
            return value.strip()
        return value


class OrderCreate(OrderBase, BaseRequest):
    """Request schema for placing a new order at the Krusty Crab."""


class OrderCreateResponse(BaseResponse):
    """Response schema for a newly created order.

    Attributes:
        order_number (int): The auto-assigned order identifier.
        total_price (float): Total cost of all items in the order.
    """

    order_number: int
    total_price: float = Field(ge=0)


class OrderFilter(BaseModel):
    """Optional filter parameters for the GET /orders endpoint.

    Attributes:
        status (Optional[OrderStatus]): Filter by order lifecycle status.
        orderer_name (Optional[str]): Filter by partial orderer name match.
    """

    status: Optional[OrderStatus] = None
    orderer_name: Optional[str] = Field(default=None, max_length=100)


class OrderListResponse(BaseResponse):
    """Response schema for an order in list view.

    Attributes:
        order_number (int): The auto-assigned order identifier.
        orderer_name (str): The name of the customer who placed the order.
        items (List[str]): Names of the ordered menu items.
        total_price (float): Total cost of all items in the order.
    """

    order_number: int
    orderer_name: str
    items: List[str]
    total_price: float = Field(ge=0)


class OrderResponse(OrderBase, BaseResponse):
    """Response schema for a Krusty Crab order.

    Attributes:
        order_number (int): The auto-assigned order identifier.
        item_price_snapshot (List[float]): Prices at time of ordering.
        total_price (float): Total cost of all items.
        status (OrderStatus): Current order lifecycle status.
        updated_at (datetime): When the order was last modified.
    """

    order_number: int
    item_price_snapshot: List[float]
    total_price: float = Field(ge=0)
    status: OrderStatus
    updated_at: datetime


class OrderStatusUpdate(BaseRequest):
    """Request schema for updating an order's lifecycle status.

    Attributes:
        status (OrderStatus): The new status to transition the order to.
    """

    status: OrderStatus


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


class OrderUpdateResponse(BaseResponse):
    """Response schema for an updated order.

    Attributes:
        order_number (int): The auto-assigned order identifier.
        total_price (float): Updated total cost of all items in the order.
    """

    order_number: int
    total_price: float = Field(ge=0)
