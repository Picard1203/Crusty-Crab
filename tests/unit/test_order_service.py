"""Unit tests for OrderService."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from bson import ObjectId

from src.enums import OrderStatus, UserRole
from src.exceptions import (
    AuthorizationError,
    InvalidStatusTransitionError,
    NotFoundError,
    OrderNotModifiableError,
)
from src.models.order_document import OrderDocument
from src.models.user_document import UserDocument
from src.schemas.order_models import OrderCreate, OrderStatusUpdate, OrderUpdate
from src.services.order_service import OrderService


def _make_user(
    username: str = "testuser",
    role: UserRole = UserRole.WORKER,
) -> UserDocument:
    """Build a UserDocument for testing.

    Args:
        username (str): The username.
        role (UserRole): The user role.

    Returns:
        UserDocument: A test user document.
    """
    return UserDocument.model_construct(
        id=ObjectId(),
        username=username,
        email=f"{username}@example.com",
        hashed_password="hashed",
        role=role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )


def _make_order(
    order_number: int = 1,
    orderer_name: str = "testuser",
    status: OrderStatus = OrderStatus.ORDER_RECEIVED,
) -> OrderDocument:
    """Build an OrderDocument for testing.

    Args:
        order_number (int): The order number.
        orderer_name (str): The username who placed the order.
        status (OrderStatus): The order status.

    Returns:
        OrderDocument: A test order document.
    """
    now = datetime.now(timezone.utc)
    return OrderDocument.model_construct(
        id=ObjectId(),
        order_number=order_number,
        orderer_name=orderer_name,
        items=["Schnitzel Alef"],
        item_price_snapshot=[66.0],
        total_price=66.0,
        status=status,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
class TestCreateOrder:
    """Tests for OrderService.create_order."""

    async def test_creates_order_successfully(
        self,
        mock_order_repo: AsyncMock,
        mock_order_factory: AsyncMock,
    ) -> None:
        """Valid create request produces an order with correct owner.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_order_factory (AsyncMock): Mocked order factory.
        """
        user = _make_user()
        order = _make_order(orderer_name=user.username)
        mock_order_factory.create.return_value = order
        mock_order_repo.create.return_value = order
        service = OrderService(mock_order_repo, mock_order_factory)
        data = OrderCreate(orderer_name="ignored", items=["Schnitzel Alef"])
        result = await service.create_order(data, user)
        assert result.orderer_name == user.username
        mock_order_factory.create.assert_called_once()


@pytest.mark.asyncio
class TestGetOrder:
    """Tests for OrderService.get_order."""

    async def test_returns_order_when_found(
        self,
        mock_order_repo: AsyncMock,
        mock_order_factory: AsyncMock,
    ) -> None:
        """Found order is returned for a worker.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_order_factory (AsyncMock): Mocked order factory.
        """
        user = _make_user(role=UserRole.WORKER)
        order = _make_order()
        mock_order_repo.get_by_order_number.return_value = order
        service = OrderService(mock_order_repo, mock_order_factory)
        result = await service.get_order(1, user)
        assert result.order_number == 1

    async def test_raises_not_found(
        self,
        mock_order_repo: AsyncMock,
        mock_order_factory: AsyncMock,
    ) -> None:
        """Missing order raises NotFoundError.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_order_factory (AsyncMock): Mocked order factory.
        """
        mock_order_repo.get_by_order_number.return_value = None
        service = OrderService(mock_order_repo, mock_order_factory)
        user = _make_user(role=UserRole.WORKER)
        with pytest.raises(NotFoundError):
            await service.get_order(999, user)

    async def test_guest_cannot_access_others_order(
        self,
        mock_order_repo: AsyncMock,
        mock_order_factory: AsyncMock,
    ) -> None:
        """Guest accessing another user's order raises AuthorizationError.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_order_factory (AsyncMock): Mocked order factory.
        """
        guest = _make_user(username="guest1", role=UserRole.GUEST)
        order = _make_order(orderer_name="other_user")
        mock_order_repo.get_by_order_number.return_value = order
        service = OrderService(mock_order_repo, mock_order_factory)
        with pytest.raises(AuthorizationError):
            await service.get_order(1, guest)

    async def test_guest_can_access_own_order(
        self,
        mock_order_repo: AsyncMock,
        mock_order_factory: AsyncMock,
    ) -> None:
        """Guest can access their own order.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_order_factory (AsyncMock): Mocked order factory.
        """
        guest = _make_user(username="guest1", role=UserRole.GUEST)
        order = _make_order(orderer_name="guest1")
        mock_order_repo.get_by_order_number.return_value = order
        service = OrderService(mock_order_repo, mock_order_factory)
        result = await service.get_order(1, guest)
        assert result.orderer_name == "guest1"


@pytest.mark.asyncio
class TestUpdateOrder:
    """Tests for OrderService.update_order."""

    async def test_raises_not_modifiable_for_complete_order(
        self,
        mock_order_repo: AsyncMock,
        mock_order_factory: AsyncMock,
    ) -> None:
        """Updating a complete order raises OrderNotModifiableError.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_order_factory (AsyncMock): Mocked order factory.
        """
        user = _make_user(role=UserRole.WORKER)
        order = _make_order(status=OrderStatus.ORDER_COMPLETE)
        mock_order_repo.get_by_order_number.return_value = order
        service = OrderService(mock_order_repo, mock_order_factory)
        data = OrderUpdate(items=["Lazanja"])
        with pytest.raises(OrderNotModifiableError):
            await service.update_order(1, data, user)

    async def test_raises_not_modifiable_for_cancelled_order(
        self,
        mock_order_repo: AsyncMock,
        mock_order_factory: AsyncMock,
    ) -> None:
        """Updating a cancelled order raises OrderNotModifiableError.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_order_factory (AsyncMock): Mocked order factory.
        """
        user = _make_user(role=UserRole.WORKER)
        order = _make_order(status=OrderStatus.ORDER_CANCELLED)
        mock_order_repo.get_by_order_number.return_value = order
        service = OrderService(mock_order_repo, mock_order_factory)
        data = OrderUpdate(items=["Lazanja"])
        with pytest.raises(OrderNotModifiableError):
            await service.update_order(1, data, user)


@pytest.mark.asyncio
class TestUpdateOrderStatus:
    """Tests for OrderService.update_order_status."""

    async def test_valid_transition_succeeds(
        self,
        mock_order_repo: AsyncMock,
        mock_order_factory: AsyncMock,
    ) -> None:
        """Worker can advance order from received to confirmed.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_order_factory (AsyncMock): Mocked order factory.
        """
        worker = _make_user(role=UserRole.WORKER)
        order = _make_order(status=OrderStatus.ORDER_RECEIVED)
        updated = _make_order(status=OrderStatus.ORDER_CONFIRMED)
        mock_order_repo.get_by_order_number.return_value = order
        mock_order_repo.update.return_value = updated
        service = OrderService(mock_order_repo, mock_order_factory)
        data = OrderStatusUpdate(status=OrderStatus.ORDER_CONFIRMED)
        result = await service.update_order_status(1, data, worker)
        assert result.status == OrderStatus.ORDER_CONFIRMED

    async def test_invalid_transition_raises(
        self,
        mock_order_repo: AsyncMock,
        mock_order_factory: AsyncMock,
    ) -> None:
        """Invalid status transition raises InvalidStatusTransitionError.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_order_factory (AsyncMock): Mocked order factory.
        """
        worker = _make_user(role=UserRole.WORKER)
        order = _make_order(status=OrderStatus.ORDER_RECEIVED)
        mock_order_repo.get_by_order_number.return_value = order
        service = OrderService(mock_order_repo, mock_order_factory)
        data = OrderStatusUpdate(status=OrderStatus.ORDER_COMPLETE)
        with pytest.raises(InvalidStatusTransitionError):
            await service.update_order_status(1, data, worker)

    async def test_admin_can_bypass_transition_check(
        self,
        mock_order_repo: AsyncMock,
        mock_order_factory: AsyncMock,
    ) -> None:
        """Administrator can make any status transition.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_order_factory (AsyncMock): Mocked order factory.
        """
        admin = _make_user(role=UserRole.ADMINISTRATOR)
        order = _make_order(status=OrderStatus.ORDER_RECEIVED)
        updated = _make_order(status=OrderStatus.ORDER_COMPLETE)
        mock_order_repo.get_by_order_number.return_value = order
        mock_order_repo.update.return_value = updated
        service = OrderService(mock_order_repo, mock_order_factory)
        data = OrderStatusUpdate(status=OrderStatus.ORDER_COMPLETE)
        result = await service.update_order_status(1, data, admin)
        assert result.status == OrderStatus.ORDER_COMPLETE
