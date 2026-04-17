"""Module containing Composition root."""

import logging
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from src.auth.password_handler import PasswordHandler
from src.auth.token_handler import TokenHandler
from src.database import Database
from src.enums import UserRole
from src.exceptions import AuthorizationError
from src.factories import MenuItemFactory, OrderFactory
from src.models import UserDocument
from src.repositories import (
    CounterRepository,
    MenuItemRepository,
    OrderRepository,
    UserRepository,
)
from src.repositories.mongodb import (
    MongoCounterRepository,
    MongoMenuItemRepository,
    MongoOrderRepository,
    MongoUserRepository,
)
from src.services import (
    AuthService,
    MenuItemService,
    OrderService,
    UserService,
)
from src.settings import get_settings

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_database(request: Request) -> Database:
    """Retrieve the database instance from application state.

    Args:
        request (Request): The incoming FastAPI request (provides app access).

    Returns:
        Database: The abstract database interface.
    """
    return request.app.state.database


def get_counter_repository() -> CounterRepository:
    """Create the counter repository.

    Returns:
        CounterRepository: The concrete counter repository.
    """
    return MongoCounterRepository()


def get_order_repository() -> OrderRepository:
    """Create the order repository.

    Returns:
        OrderRepository: The concrete order repository.
    """
    return MongoOrderRepository()


def get_menu_item_repository() -> MenuItemRepository:
    """Create the menu item repository.

    Returns:
        MenuItemRepository: The concrete menu item repository.
    """
    return MongoMenuItemRepository()


def get_user_repository() -> UserRepository:
    """Create the user repository.

    Returns:
        UserRepository: The concrete user repository.
    """
    return MongoUserRepository()


def get_password_handler() -> PasswordHandler:
    """Create the password handler.

    Returns:
        PasswordHandler: The bcrypt password handler.
    """
    return PasswordHandler()


def get_token_handler() -> TokenHandler:
    """Create the token handler with settings.

    Returns:
        TokenHandler: The JWT token handler.
    """
    return TokenHandler(get_settings())


def get_order_factory(
    counter_repo: Annotated[CounterRepository, Depends(get_counter_repository)],
    menu_item_repo: Annotated[
        MenuItemRepository, Depends(get_menu_item_repository)
    ],
) -> OrderFactory:
    """Create the order factory with its dependencies.

    Args:
        counter_repo (CounterRepository): Injected counter repository.
        menu_item_repo (MenuItemRepository): Injected menu item repository.

    Returns:
        OrderFactory: The order document factory.
    """
    return OrderFactory(counter_repo, menu_item_repo)


def get_menu_item_factory(
    counter_repo: Annotated[CounterRepository, Depends(get_counter_repository)],
) -> MenuItemFactory:
    """Create the menu item factory with its dependencies.

    Args:
        counter_repo (CounterRepository): Injected counter repository.

    Returns:
        MenuItemFactory: The menu item document factory.
    """
    return MenuItemFactory(counter_repo)


def get_order_service(
    repository: Annotated[OrderRepository, Depends(get_order_repository)],
    factory: Annotated[OrderFactory, Depends(get_order_factory)],
) -> OrderService:
    """Create the order service with its dependencies.

    Args:
        repository (OrderRepository): Injected order repository.
        factory (OrderFactory): Injected order factory.

    Returns:
        OrderService: The order business logic service.
    """
    return OrderService(repository, factory)


def get_menu_item_service(
    repository: Annotated[
        MenuItemRepository, Depends(get_menu_item_repository)
    ],
    factory: Annotated[MenuItemFactory, Depends(get_menu_item_factory)],
) -> MenuItemService:
    """Create the menu item service with its dependencies.

    Args:
        repository (MenuItemRepository): Injected menu item repository.
        factory (MenuItemFactory): Injected menu item factory.

    Returns:
        MenuItemService: The menu item business logic service.
    """
    return MenuItemService(repository, factory)


def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    password_handler: Annotated[PasswordHandler, Depends(get_password_handler)],
    token_handler: Annotated[TokenHandler, Depends(get_token_handler)],
) -> AuthService:
    """Create the auth service with its dependencies.

    Args:
        user_repo (UserRepository): Injected user repository.
        password_handler (PasswordHandler): Injected password handler.
        token_handler (TokenHandler): Injected token handler.

    Returns:
        AuthService: The authentication business logic service.
    """
    return AuthService(user_repo, password_handler, token_handler)


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """Create the user service with its dependencies.

    Args:
        repository (UserRepository): Injected user repository.

    Returns:
        UserService: The user management business logic service.
    """
    return UserService(repository)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserDocument:
    """Resolve the current user from the bearer token.

    Args:
        token (str): The bearer token extracted by OAuth2PasswordBearer.
        auth_service (AuthService): Injected auth service.

    Returns:
        UserDocument: The authenticated user.

    Raises:
        AuthenticationError: If the token is invalid or user not found.
    """
    return await auth_service.get_current_user(token)


async def require_worker(
    current_user: Annotated[UserDocument, Depends(get_current_user)],
) -> UserDocument:
    """Require the current user to have worker or administrator role.

    Args:
        current_user (UserDocument): The authenticated user.

    Returns:
        UserDocument: The authenticated user if authorized.

    Raises:
        AuthorizationError: If the user is not a worker or administrator.
    """
    if current_user.role not in (UserRole.WORKER, UserRole.ADMINISTRATOR):
        raise AuthorizationError("Worker or administrator role required")
    return current_user


async def require_administrator(
    current_user: Annotated[UserDocument, Depends(get_current_user)],
) -> UserDocument:
    """Require the current user to have administrator role.

    Args:
        current_user (UserDocument): The authenticated user.

    Returns:
        UserDocument: The authenticated user if authorized.

    Raises:
        AuthorizationError: If the user is not an administrator.
    """
    if current_user.role != UserRole.ADMINISTRATOR:
        raise AuthorizationError("Administrator role required")
    return current_user
