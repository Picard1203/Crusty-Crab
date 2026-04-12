"""Order status enumeration for the Krusty Crab order lifecycle."""

from enum import Enum


class OrderStatus(str, Enum):
    """Represents all possible states an order can be in.

    Attributes:
        ORDER_RECEIVED: The order has been placed by the customer.
        ORDER_CONFIRMED: The order has been confirmed by staff.
        ORDER_BEING_PREPARED: The kitchen is preparing the order.
        ORDER_READY: The order is ready for pickup or delivery.
        ORDER_COMPLETE: The order has been delivered and completed.
        ORDER_CANCELLED: The order has been cancelled.
    """

    ORDER_RECEIVED = "order_received"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_BEING_PREPARED = "order_being_prepared"
    ORDER_READY = "order_ready"
    ORDER_COMPLETE = "order_complete"
    ORDER_CANCELLED = "order_cancelled"
