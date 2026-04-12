"""Schema for order creation requests."""

from src.schemas.base_request import BaseRequest
from src.schemas.order.order_base import OrderBase


class OrderCreate(OrderBase, BaseRequest):
    """Request schema for placing a new order at the Krusty Crab."""
