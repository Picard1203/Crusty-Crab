"""Schema for order status breakdown response."""

from pydantic import BaseModel

from src.enums import OrderStatus


class OrderStatusBreakdownResponse(BaseModel):
    """Response schema for count of orders per status.

    Attributes:
        status (OrderStatus): The order lifecycle status.
        count (int): Number of orders in this status.
    """

    status: OrderStatus
    count: int
