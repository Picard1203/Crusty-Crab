"""Schema for daily profits summary response."""

from pydantic import BaseModel


class DailyProfitsResponse(BaseModel):
    """Response schema for daily profit aggregation.

    Attributes:
        total (float): Cumulative profit across all orders.
        daily_average (float): Average profit per active order day.
    """

    total: float
    daily_average: float
