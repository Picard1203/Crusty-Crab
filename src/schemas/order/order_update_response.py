"""Response schema for updated orders."""

from pydantic import Field

from src.schemas.base_response import BaseResponse


class OrderUpdateResponse(BaseResponse):
    """Response schema for an updated order.

    Attributes:
        order_number (int): The auto-assigned order identifier.
        total_price (float): Updated total cost of all items in the order.
    """

    order_number: int
    total_price: float = Field(ge=0)
