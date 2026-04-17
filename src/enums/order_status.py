"""Order status enumeration for the Krusty Crab order lifecycle."""

from enum import Enum


class OrderStatus(str, Enum):
    """Represents all possible states an order can be in."""

    ORDER_RECEIVED = "order_received"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_BEING_PREPARED = "order_being_prepared"
    ORDER_READY = "order_ready"
    ORDER_COMPLETE = "order_complete"
    ORDER_CANCELLED = "order_cancelled"
