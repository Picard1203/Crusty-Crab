"""Statistics response schemas."""

from typing import Optional

from pydantic import BaseModel

from src.enums import OrderStatus


class BusiestHourResponse(BaseModel):
    """Response schema for the hour with the most orders.

    Attributes:
        hour (int): The hour of the day (0-23) with the most orders.
        order_count (int): Number of orders placed during that hour.
    """

    hour: int
    order_count: int


class DailyProfitsResponse(BaseModel):
    """Response schema for daily profit aggregation.

    Attributes:
        total (float): Cumulative profit across all orders.
        daily_average (float): Average profit per active order day.
    """

    total: float
    daily_average: float


class OrderStatusBreakdownResponse(BaseModel):
    """Response schema for count of orders per status.

    Attributes:
        status (OrderStatus): The order lifecycle status.
        count (int): Number of orders in this status.
    """

    status: OrderStatus
    count: int


class StatisticsResponse(BaseModel):
    """Generic response schema for a single aggregated statistic.

    Attributes:
        value (float): The numeric statistic value.
        label (Optional[str]): Optional label (e.g., item name).
    """

    value: float
    label: Optional[str] = None


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
