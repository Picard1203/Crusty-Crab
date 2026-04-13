"""Order CRUD and status management endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.deps import get_current_user, get_order_service, require_worker
from src.models import UserDocument
from src.schemas import (
    OrderCreate,
    OrderCreateResponse,
    OrderFilter,
    OrderListResponse,
    OrderResponse,
    OrderStatusUpdate,
    OrderUpdate,
    OrderUpdateResponse,
    PaginatedResponse,
)
from src.services import OrderService
from src.settings import get_settings

_settings = get_settings()

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/",
    response_model=OrderCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    data: OrderCreate,
    service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[UserDocument, Depends(get_current_user)],
) -> OrderCreateResponse:
    """Place a new order at the Krusty Crab.

    Args:
        data (OrderCreate): The order payload with item names.
        service (OrderService): Injected order service.
        current_user (UserDocument): The authenticated user placing the order.

    Returns:
        OrderCreateResponse: The order_number and total_price of the new order.
    """
    logger.info("POST /orders")
    return await service.create_order(data, current_user)


@router.get(
    "/",
    response_model=PaginatedResponse[OrderListResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_orders(
    service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[UserDocument, Depends(get_current_user)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(
        default=_settings.pagination_default_limit,
        ge=1,
        le=_settings.pagination_max_limit,
    ),
    filters: OrderFilter = Depends(),
) -> PaginatedResponse[OrderListResponse]:
    """Retrieve a paginated list of orders.

    Args:
        service (OrderService): Injected order service.
        current_user (UserDocument): The authenticated requesting user.
        skip (int): Pagination offset.
        limit (int): Pagination page size.
        filters (OrderFilter): Optional query parameter filters.

    Returns:
        PaginatedResponse[OrderListResponse]: Paginated order list.
    """
    logger.info(f"GET /orders skip={skip} limit={limit}")
    return await service.get_all_orders(skip, limit, filters, current_user)


@router.get(
    "/{order_number}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
)
async def get_order(
    order_number: int,
    service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[UserDocument, Depends(get_current_user)],
) -> OrderResponse:
    """Retrieve a single order by its number.

    Args:
        order_number (int): The auto-assigned order identifier.
        service (OrderService): Injected order service.
        current_user (UserDocument): The authenticated requesting user.

    Returns:
        OrderResponse: The order data.
    """
    logger.info(f"GET /orders/{order_number}")
    return await service.get_order(order_number, current_user)


@router.put(
    "/{order_number}",
    response_model=OrderUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_order(
    order_number: int,
    data: OrderUpdate,
    service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[UserDocument, Depends(get_current_user)],
) -> OrderUpdateResponse:
    """Update an existing order's details.

    Args:
        order_number (int): The order to update.
        data (OrderUpdate): The fields to update.
        service (OrderService): Injected order service.
        current_user (UserDocument): The authenticated requesting user.

    Returns:
        OrderUpdateResponse: The order_number and updated total_price.
    """
    logger.info(f"PUT /orders/{order_number}")
    return await service.update_order(order_number, data, current_user)


@router.delete(
    "/{order_number}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order(
    order_number: int,
    service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[UserDocument, Depends(get_current_user)],
) -> None:
    """Delete an order by its number.

    Args:
        order_number (int): The order to delete.
        service (OrderService): Injected order service.
        current_user (UserDocument): The authenticated requesting user.
    """
    logger.info(f"DELETE /orders/{order_number}")
    await service.delete_order(order_number, current_user)


@router.patch(
    "/{order_number}/status",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
)
async def update_order_status(
    order_number: int,
    data: OrderStatusUpdate,
    service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[UserDocument, Depends(require_worker)],
) -> OrderResponse:
    """Update an order's lifecycle status.

    Args:
        order_number (int): The order to update.
        data (OrderStatusUpdate): The new status.
        service (OrderService): Injected order service.
        current_user (UserDocument): The authenticated worker or administrator.

    Returns:
        OrderResponse: The order with updated status.
    """
    logger.info(f"PATCH /orders/{order_number}/status to {data.status}")
    return await service.update_order_status(order_number, data, current_user)
