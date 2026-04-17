"""Unit test fixtures — mock repositories, factories, and auth handlers."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.auth.password_handler import PasswordHandler
from src.auth.token_handler import TokenHandler
from src.factories.menu_item_factory import MenuItemFactory
from src.factories.order_factory import OrderFactory
from src.models import (
    CounterDocument,
    MenuItemDocument,
    OrderDocument,
    UserDocument,
)
from src.repositories.counter_repository import CounterRepository
from src.repositories.menu_item_repository import MenuItemRepository
from src.repositories.order_repository import OrderRepository
from src.repositories.user_repository import UserRepository
from src.settings import get_settings


@pytest.fixture
def mock_order_repo() -> AsyncMock:
    """Create a mocked OrderRepository.

    Returns:
        AsyncMock: The mocked repository.
    """
    return AsyncMock(spec=OrderRepository)


@pytest.fixture
def mock_menu_item_repo() -> AsyncMock:
    """Create a mocked MenuItemRepository.

    Returns:
        AsyncMock: The mocked repository.
    """
    return AsyncMock(spec=MenuItemRepository)


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    """Create a mocked UserRepository.

    Returns:
        AsyncMock: The mocked repository.
    """
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_counter_repo() -> AsyncMock:
    """Create a mocked CounterRepository.

    Returns:
        AsyncMock: The mocked repository.
    """
    mock = AsyncMock(spec=CounterRepository)
    mock.get_next_sequence.return_value = 1
    return mock


@pytest.fixture
def mock_order_factory(mock_counter_repo: AsyncMock) -> AsyncMock:  # noqa: ARG001
    """Create a mocked OrderFactory.

    Args:
        mock_counter_repo (AsyncMock): The mocked counter repository.

    Returns:
        AsyncMock: The mocked factory.
    """
    return AsyncMock(spec=OrderFactory)


@pytest.fixture
def mock_menu_item_factory(mock_counter_repo: AsyncMock) -> AsyncMock:  # noqa: ARG001
    """Create a mocked MenuItemFactory.

    Args:
        mock_counter_repo (AsyncMock): The mocked counter repository.

    Returns:
        AsyncMock: The mocked factory.
    """
    return AsyncMock(spec=MenuItemFactory)


@pytest.fixture
def password_handler() -> PasswordHandler:
    """Create a real PasswordHandler (no external deps to mock).

    Returns:
        PasswordHandler: The password handler.
    """
    return PasswordHandler()


@pytest.fixture
def token_handler() -> TokenHandler:
    """Create a real TokenHandler with test settings.

    Returns:
        TokenHandler: The token handler.
    """
    return TokenHandler(get_settings())


@pytest.fixture(autouse=True)
def mock_beanie_document_settings():
    """Mock Beanie document settings so Documents can be instantiated without MongoDB.

    Yields:
        None: Control to the test function.
    """
    _doc_classes = [
        CounterDocument,
        MenuItemDocument,
        OrderDocument,
        UserDocument,
    ]
    mock_settings = MagicMock()
    originals = {cls: cls._document_settings for cls in _doc_classes}
    for cls in _doc_classes:
        cls._document_settings = mock_settings
    yield
    for cls, original in originals.items():
        cls._document_settings = original
