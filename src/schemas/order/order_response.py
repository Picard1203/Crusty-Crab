"""Schema for order response payloads."""

from datetime import datetime
from typing import List

from pydantic import Field

from src.enums import OrderStatus
from src.schemas.base_response import BaseResponse
from src.schemas.order.order_base import OrderBase


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
