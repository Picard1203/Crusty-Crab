"""Order MongoDB document model."""

from datetime import datetime, timezone
from typing import ClassVar, List

from beanie import Indexed
from pydantic import Field

from src.enums import OrderStatus
from src.models.base_document import BaseDocument


class OrderDocument(BaseDocument):
    """MongoDB document model for a Krusty Crab order.

    Attributes:
        order_number (int): Unique auto-increment order identifier.
        orderer_name (str): The username of the customer who placed the order.
        items (List[str]): Names of the ordered menu items.
        item_price_snapshot (List[float]): Prices of items at time of order.
            Parallel array to items — preserves pricing history.
        total_price (float): Sum of item_price_snapshot at order time.
        status (OrderStatus): Current lifecycle status of the order.
            Defaults to ORDER_RECEIVED.
        updated_at (datetime): Timestamp of the last update.
            Defaults to current UTC time.
    """

    order_number: Indexed(int, unique=True)  # type: ignore
    orderer_name: str
    items: List[str]
    item_price_snapshot: List[float]
    total_price: float = Field(ge=0)
    status: OrderStatus = OrderStatus.ORDER_RECEIVED
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        """Beanie document configuration."""

        name = "orders"
        indexes: ClassVar[list] = [
            "status",
            "created_at",
            "orderer_name",
        ]
