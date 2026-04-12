"""Response schema for orders in list view."""

from typing import List

from pydantic import Field

from src.schemas.base_response import BaseResponse


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
