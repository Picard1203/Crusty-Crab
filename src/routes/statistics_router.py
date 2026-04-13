"""Statistics and profits endpoints."""

import logging
from datetime import date
from typing import Annotated, List

from fastapi import APIRouter, Depends, Query, status

from src.deps import (
    get_menu_item_repository,
    get_order_repository,
    require_administrator,
)
from src.repositories import MenuItemRepository, OrderRepository
from src.schemas import (
    BusiestHourResponse,
    DailyProfitsResponse,
    OrderStatusBreakdownResponse,
    StatisticsResponse,
    TopCustomerResponse,
)
from src.services import StatisticsService

logger = logging.getLogger(__name__)


def get_statistics_service(
    order_repo: Annotated[OrderRepository, Depends(get_order_repository)],
    menu_item_repo: Annotated[
        MenuItemRepository, Depends(get_menu_item_repository)
    ],
) -> StatisticsService:
    """Create the statistics service with its dependencies.

    Args:
        order_repo (OrderRepository): Injected order repository.
        menu_item_repo (MenuItemRepository): Injected menu item repository.

    Returns:
        StatisticsService: The statistics business logic service.
    """
    return StatisticsService(order_repo, menu_item_repo)


profits_router = APIRouter(
    prefix="/profits",
    tags=["Profits"],
    dependencies=[Depends(require_administrator)],
)

statistics_router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"],
    dependencies=[Depends(require_administrator)],
)


@profits_router.get(
    "/",
    response_model=StatisticsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_total_profits(
    service: Annotated[StatisticsService, Depends(get_statistics_service)],
) -> StatisticsResponse:
    """Retrieve total restaurant profits across all orders.

    Args:
        service (StatisticsService): Injected statistics service.

    Returns:
        StatisticsResponse: Total profits value.
    """
    logger.info("GET /profits")
    return await service.get_total_profits()


@profits_router.get(
    "/daily-average",
    response_model=DailyProfitsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_daily_average_profits(
    service: Annotated[StatisticsService, Depends(get_statistics_service)],
) -> DailyProfitsResponse:
    """Retrieve total profits and average daily profit.

    Args:
        service (StatisticsService): Injected statistics service.

    Returns:
        DailyProfitsResponse: Total profits and daily average.
    """
    logger.info("GET /profits/daily-average")
    return await service.get_daily_average_profits()


@profits_router.get(
    "/by-date",
    response_model=StatisticsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_profits_by_date(
    service: Annotated[StatisticsService, Depends(get_statistics_service)],
    target_date: date = Query(alias="date"),
) -> StatisticsResponse:
    """Retrieve total profits for a specific calendar day.

    Args:
        service (StatisticsService): Injected statistics service.
        target_date (date): The date to query in YYYY-MM-DD format.

    Returns:
        StatisticsResponse: Profits for the specified date.
    """
    logger.info(f"GET /profits/by-date date={target_date}")
    return await service.get_profits_by_date(target_date)


@statistics_router.get(
    "/most-profitable-item",
    response_model=StatisticsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_most_profitable_item(
    service: Annotated[StatisticsService, Depends(get_statistics_service)],
) -> StatisticsResponse:
    """Retrieve the menu item with the highest total revenue.

    Args:
        service (StatisticsService): Injected statistics service.

    Returns:
        StatisticsResponse: Item name (label) and total revenue (value).
    """
    logger.info("GET /statistics/most-profitable-item")
    return await service.get_most_profitable_item()


@statistics_router.get(
    "/least-profitable-item",
    response_model=StatisticsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_least_profitable_item(
    service: Annotated[StatisticsService, Depends(get_statistics_service)],
) -> StatisticsResponse:
    """Retrieve the menu item with the lowest total revenue.

    Args:
        service (StatisticsService): Injected statistics service.

    Returns:
        StatisticsResponse: Item name (label) and total revenue (value).
    """
    logger.info("GET /statistics/least-profitable-item")
    return await service.get_least_profitable_item()


@statistics_router.get(
    "/orders-by-status",
    response_model=List[OrderStatusBreakdownResponse],
    status_code=status.HTTP_200_OK,
)
async def get_orders_by_status(
    service: Annotated[StatisticsService, Depends(get_statistics_service)],
) -> List[OrderStatusBreakdownResponse]:
    """Retrieve order counts grouped by status.

    Args:
        service (StatisticsService): Injected statistics service.

    Returns:
        List[OrderStatusBreakdownResponse]: Per-status order counts.
    """
    logger.info("GET /statistics/orders-by-status")
    return await service.get_orders_by_status()


@statistics_router.get(
    "/busiest-hour",
    response_model=BusiestHourResponse,
    status_code=status.HTTP_200_OK,
)
async def get_busiest_hour(
    service: Annotated[StatisticsService, Depends(get_statistics_service)],
) -> BusiestHourResponse:
    """Retrieve the hour of day with the most orders.

    Args:
        service (StatisticsService): Injected statistics service.

    Returns:
        BusiestHourResponse: The busiest hour (0-23) and order count.
    """
    logger.info("GET /statistics/busiest-hour")
    return await service.get_busiest_hour()


@statistics_router.get(
    "/average-order-size",
    response_model=StatisticsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_average_order_size(
    service: Annotated[StatisticsService, Depends(get_statistics_service)],
) -> StatisticsResponse:
    """Retrieve the average number of items per order.

    Args:
        service (StatisticsService): Injected statistics service.

    Returns:
        StatisticsResponse: Average item count per order.
    """
    logger.info("GET /statistics/average-order-size")
    return await service.get_average_order_size()


@statistics_router.get(
    "/top-customers",
    response_model=List[TopCustomerResponse],
    status_code=status.HTTP_200_OK,
)
async def get_top_customers(
    service: Annotated[StatisticsService, Depends(get_statistics_service)],
    limit: int = Query(default=10, ge=1, le=100),
) -> List[TopCustomerResponse]:
    """Retrieve the top customers ranked by total spend.

    Args:
        service (StatisticsService): Injected statistics service.
        limit (int): Maximum number of customers to return (1-100).

    Returns:
        List[TopCustomerResponse]: Top customers with spend data.
    """
    logger.info(f"GET /statistics/top-customers limit={limit}")
    return await service.get_top_customers(limit)
