"""Business logic for statistics and profit aggregation operations."""

import logging
from datetime import date, datetime, timezone
from typing import List

from src.repositories import MenuItemRepository, OrderRepository
from src.schemas import (
    BusiestHourResponse,
    DailyProfitsResponse,
    OrderStatusBreakdownResponse,
    StatisticsResponse,
    TopCustomerResponse,
)

logger = logging.getLogger(__name__)


class StatisticsService:
    """Orchestrates statistics and profit aggregation business logic.

    Attributes:
        _order_repo (OrderRepository): Order data access and aggregations.
        _menu_item_repo (MenuItemRepository): Menu item data access.
    """

    def __init__(
        self,
        order_repo: OrderRepository,
        menu_item_repo: MenuItemRepository,
    ) -> None:
        """Initialize with repository dependencies.

        Args:
            order_repo (OrderRepository): The order repository interface.
            menu_item_repo (MenuItemRepository): The menu item repository.
        """
        self._order_repo: OrderRepository = order_repo
        self._menu_item_repo: MenuItemRepository = menu_item_repo

    async def get_total_profits(self) -> StatisticsResponse:
        """Calculate total restaurant profits across all orders.

        Returns:
            StatisticsResponse: The aggregate total profit value.
        """
        logger.info("Fetching total profits")
        total = await self._order_repo.sum_total_price({})
        return StatisticsResponse(value=total)

    async def get_daily_average_profits(self) -> DailyProfitsResponse:
        """Calculate average daily profit across all active order days.

        Returns:
            DailyProfitsResponse: Total profits and daily average.
        """
        logger.info("Fetching daily average profits")
        total = await self._order_repo.sum_total_price({})
        distinct_days = await self._order_repo.count_distinct_order_days()
        if distinct_days == 0:
            average = 0.0
        else:
            average = total / distinct_days
        return DailyProfitsResponse(total=total, daily_average=average)

    async def get_profits_by_date(
        self, target_date: date
    ) -> StatisticsResponse:
        """Calculate total profits for a specific calendar day.

        Args:
            target_date (date): The calendar day to aggregate.

        Returns:
            StatisticsResponse: Total profits for the given day.
        """
        logger.info(f"Fetching profits for date {target_date}")
        start = datetime(
            target_date.year,
            target_date.month,
            target_date.day,
            tzinfo=timezone.utc,
        )
        end = datetime(
            target_date.year,
            target_date.month,
            target_date.day,
            23,
            59,
            59,
            999999,
            tzinfo=timezone.utc,
        )
        filters = {"created_at": {"$gte": start, "$lte": end}}
        total = await self._order_repo.sum_total_price(filters)
        return StatisticsResponse(value=total)

    async def get_most_profitable_item(self) -> StatisticsResponse:
        """Find the menu item that has generated the most revenue.

        Returns:
            StatisticsResponse: The item name and its total revenue.
        """
        logger.info("Fetching most profitable item")
        items = await self._order_repo.aggregate_item_profitability()
        if len(items) == 0:
            return StatisticsResponse(value=0.0, label="N/A")
        most_profitable = max(items, key=lambda item: item["total_revenue"])
        return StatisticsResponse(
            value=most_profitable["total_revenue"],
            label=most_profitable["name"],
        )

    async def get_least_profitable_item(self) -> StatisticsResponse:
        """Find the menu item that has generated the least revenue.

        Returns:
            StatisticsResponse: The item name and its total revenue.
        """
        logger.info("Fetching least profitable item")
        items = await self._order_repo.aggregate_item_profitability()
        if len(items) == 0:
            return StatisticsResponse(value=0.0, label="N/A")
        least_profitable = min(items, key=lambda item: item["total_revenue"])
        return StatisticsResponse(
            value=least_profitable["total_revenue"],
            label=least_profitable["name"],
        )

    async def get_orders_by_status(self) -> List[OrderStatusBreakdownResponse]:
        """Count orders grouped by status.

        Returns:
            List[OrderStatusBreakdownResponse]: Per-status order counts.
        """
        logger.info("Fetching orders by status breakdown")
        results = await self._order_repo.aggregate_by_status()
        status_responses = []
        for row in results:
            status_responses.append(
                OrderStatusBreakdownResponse(
                    status=row["status"], count=row["count"]
                )
            )
        return status_responses

    async def get_busiest_hour(self) -> BusiestHourResponse:
        """Find the hour of day with the most orders.

        Returns:
            BusiestHourResponse: The busiest hour and its order count.
        """
        logger.info("Fetching busiest hour")
        results = await self._order_repo.aggregate_by_hour()
        if len(results) == 0:
            return BusiestHourResponse(hour=0, order_count=0)
        busiest_hour_data = max(
            results, key=lambda hour_data: hour_data["order_count"]
        )
        return BusiestHourResponse(
            hour=busiest_hour_data["hour"],
            order_count=busiest_hour_data["order_count"],
        )

    async def get_average_order_size(self) -> StatisticsResponse:
        """Calculate the average number of items per order.

        Returns:
            StatisticsResponse: The average item count per order.
        """
        logger.info("Fetching average order size")
        average = await self._order_repo.get_average_items_per_order()
        return StatisticsResponse(value=average)

    async def get_top_customers(self, limit: int) -> List[TopCustomerResponse]:
        """Return the top customers ranked by total spend.

        Args:
            limit (int): Maximum number of customers to return.

        Returns:
            List[TopCustomerResponse]: Top customers with spend data.
        """
        logger.info(f"Fetching top {limit} customers")
        results = await self._order_repo.aggregate_top_customers(limit)
        customer_responses = []
        for row in results:
            customer_responses.append(
                TopCustomerResponse(
                    orderer_name=row["orderer_name"],
                    order_count=row["order_count"],
                    total_spent=row["total_spent"],
                )
            )
        return customer_responses
