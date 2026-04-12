"""Query filter schema for order list endpoints."""

from typing import Optional

from pydantic import BaseModel, Field

from src.enums import OrderStatus


class OrderFilter(BaseModel):
    """Optional filter parameters for the GET /orders endpoint.

    Attributes:
        status (Optional[OrderStatus]): Filter by order lifecycle status.
        orderer_name (Optional[str]): Filter by partial orderer name match.
    """

    status: Optional[OrderStatus] = None
    orderer_name: Optional[str] = Field(default=None, max_length=100)
