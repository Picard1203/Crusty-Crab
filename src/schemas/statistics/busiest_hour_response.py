"""Schema for busiest hour statistics response."""

from pydantic import BaseModel


class BusiestHourResponse(BaseModel):
    """Response schema for the hour with the most orders.

    Attributes:
        hour (int): The hour of the day (0-23) with the most orders.
        order_count (int): Number of orders placed during that hour.
    """

    hour: int
    order_count: int
