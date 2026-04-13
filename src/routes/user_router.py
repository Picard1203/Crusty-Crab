"""Admin user management endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.deps import get_user_service, require_administrator
from src.schemas import PaginatedResponse, UserResponse, UserUpdate
from src.services import UserService
from src.settings import get_settings

_settings = get_settings()

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(require_administrator)],
)


@router.get(
    "/",
    response_model=PaginatedResponse[UserResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    service: Annotated[UserService, Depends(get_user_service)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(
        default=_settings.pagination_default_limit,
        ge=1,
        le=_settings.pagination_max_limit,
    ),
) -> PaginatedResponse[UserResponse]:
    """Retrieve a paginated list of all users.

    Args:
        service (UserService): Injected user service.
        skip (int): Pagination offset.
        limit (int): Pagination page size.

    Returns:
        PaginatedResponse[UserResponse]: Paginated list of users.
    """
    logger.info(f"GET /users skip={skip} limit={limit}")
    return await service.get_all_users(skip, limit)


@router.get(
    "/{username}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    username: str,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Retrieve a single user by username.

    Args:
        username (str): The username to look up.
        service (UserService): Injected user service.

    Returns:
        UserResponse: The user data.
    """
    logger.info(f"GET /users/{username}")
    return await service.get_user(username)


@router.put(
    "/{username}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    username: str,
    data: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Update a user's role or active status.

    Args:
        username (str): The username of the user to update.
        data (UserUpdate): The fields to update.
        service (UserService): Injected user service.

    Returns:
        UserResponse: The updated user data.
    """
    logger.info(f"PUT /users/{username}")
    return await service.update_user(username, data)


@router.delete(
    "/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    username: str,
    service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    """Permanently delete a user.

    Args:
        username (str): The username of the user to delete.
        service (UserService): Injected user service.
    """
    logger.info(f"DELETE /users/{username}")
    await service.delete_user(username)
