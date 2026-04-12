"""Response schema for newly created orders."""

from pydantic import Field

from src.schemas.base_response import BaseResponse


class OrderCreateResponse(BaseResponse):
    """Response schema for a newly created order.

    Attributes:
        order_number (int): The auto-assigned order identifier.
        total_price (float): Total cost of all items in the order.
    """

    order_number: int
    total_price: float = Field(ge=0)
