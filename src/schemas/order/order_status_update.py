"""Schema for order status update requests."""

from src.enums import OrderStatus
from src.schemas.base_request import BaseRequest


class OrderStatusUpdate(BaseRequest):
    """Request schema for updating an order's lifecycle status.

    Attributes:
        status (OrderStatus): The new status to transition the order to.
    """

    status: OrderStatus
