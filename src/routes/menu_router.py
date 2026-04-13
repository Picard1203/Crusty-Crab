"""Menu item management endpoints."""

import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, Query, status

from src.deps import (
    get_menu_item_service,
    require_administrator,
)
from src.schemas import (
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate,
    PaginatedResponse,
)
from src.services import MenuItemService
from src.settings import get_settings

_settings = get_settings()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get(
    "/",
    response_model=List[MenuItemResponse],
    status_code=status.HTTP_200_OK,
)
async def get_active_menu(
    service: Annotated[MenuItemService, Depends(get_menu_item_service)],
) -> List[MenuItemResponse]:
    """Retrieve all currently active menu items.

    Args:
        service (MenuItemService): Injected menu item service.

    Returns:
        List[MenuItemResponse]: All available menu items.
    """
    logger.info("GET /menu")
    return await service.get_active_menu()


@router.get(
    "/{item_number}",
    response_model=MenuItemResponse,
    status_code=status.HTTP_200_OK,
)
async def get_menu_item(
    item_number: int,
    service: Annotated[MenuItemService, Depends(get_menu_item_service)],
) -> MenuItemResponse:
    """Retrieve a single menu item by its number.

    Args:
        item_number (int): The auto-assigned menu item identifier.
        service (MenuItemService): Injected menu item service.

    Returns:
        MenuItemResponse: The menu item data.
    """
    logger.info(f"GET /menu/{item_number}")
    return await service.get_menu_item(item_number)


@router.post(
    "/",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_administrator)],
)
async def create_menu_item(
    data: MenuItemCreate,
    service: Annotated[MenuItemService, Depends(get_menu_item_service)],
) -> MenuItemResponse:
    """Create a new menu item.

    Args:
        data (MenuItemCreate): The menu item creation payload.
        service (MenuItemService): Injected menu item service.

    Returns:
        MenuItemResponse: The created menu item.
    """
    logger.info("POST /menu")
    return await service.create_menu_item(data)


@router.put(
    "/{item_number}",
    response_model=MenuItemResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_administrator)],
)
async def update_menu_item(
    item_number: int,
    data: MenuItemUpdate,
    service: Annotated[MenuItemService, Depends(get_menu_item_service)],
) -> MenuItemResponse:
    """Update an existing menu item.

    Args:
        item_number (int): The menu item to update.
        data (MenuItemUpdate): The fields to update.
        service (MenuItemService): Injected menu item service.

    Returns:
        MenuItemResponse: The updated menu item.
    """
    logger.info(f"PUT /menu/{item_number}")
    return await service.update_menu_item(item_number, data)


@router.delete(
    "/{item_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_administrator)],
)
async def delete_menu_item(
    item_number: int,
    service: Annotated[MenuItemService, Depends(get_menu_item_service)],
) -> None:
    """Soft-delete a menu item by marking it inactive.

    Args:
        item_number (int): The menu item to deactivate.
        service (MenuItemService): Injected menu item service.
    """
    logger.info(f"DELETE /menu/{item_number}")
    await service.delete_menu_item(item_number)


@router.get(
    "/admin/all",
    response_model=PaginatedResponse[MenuItemResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_administrator)],
)
async def get_all_menu_items(
    service: Annotated[MenuItemService, Depends(get_menu_item_service)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(
        default=_settings.pagination_default_limit,
        ge=1,
        le=_settings.pagination_max_limit,
    ),
) -> PaginatedResponse[MenuItemResponse]:
    """Retrieve all menu items including inactive ones.

    Args:
        service (MenuItemService): Injected menu item service.
        skip (int): Pagination offset.
        limit (int): Pagination page size.

    Returns:
        PaginatedResponse[MenuItemResponse]: Paginated list of all menu items.
    """
    logger.info(f"GET /menu/admin/all skip={skip} limit={limit}")
    return await service.get_all_menu_items(skip, limit)
