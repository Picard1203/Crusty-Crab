"""Schema for top customer statistics response."""

from pydantic import BaseModel


class TopCustomerResponse(BaseModel):
    """Response schema for a top-spending customer.

    Attributes:
        orderer_name (str): The customer's username.
        order_count (int): Total number of orders placed.
        total_spent (float): Cumulative spend across all orders.
    """

    orderer_name: str
    order_count: int
    total_spent: float
