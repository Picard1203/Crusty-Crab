"""Auth endpoints for register, login, refresh, and current user."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.deps import get_auth_service, get_current_user
from src.models import UserDocument
from src.schemas import (
    TokenRefreshRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from src.services import AuthService

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Register a new API user.

    Args:
        data (UserCreate): The registration payload.
        service (AuthService): Injected auth service.

    Returns:
        UserResponse: The created user data.
    """
    logger.info("POST /auth/register")
    return await service.register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("5/minute")
async def login(
    request: Request,  # noqa: ARG001
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Authenticate and receive JWT tokens.

    Args:
        request (Request): The incoming request (required by slowapi).
        form_data (OAuth2PasswordRequestForm): Username/password from form.
        service (AuthService): Injected auth service.

    Returns:
        TokenResponse: Access and refresh token pair.
    """
    logger.info("POST /auth/login")
    return await service.authenticate(form_data.username, form_data.password)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    data: TokenRefreshRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Exchange a refresh token for a new token pair.

    Args:
        data (TokenRefreshRequest): The refresh token payload.
        service (AuthService): Injected auth service.

    Returns:
        TokenResponse: New access and refresh token pair.
    """
    logger.info("POST /auth/refresh")
    return await service.refresh_token(data.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: Annotated[UserDocument, Depends(get_current_user)],
) -> UserResponse:
    """Get the currently authenticated user's info.

    Args:
        current_user (UserDocument): Resolved from the bearer token.

    Returns:
        UserResponse: The current user's data.
    """
    logger.info("GET /auth/me")
    return current_user
