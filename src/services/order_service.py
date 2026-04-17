"""Business logic for order operations."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from src.constants.order_constants import WORKER_ALLOWED_TRANSITIONS
from src.enums import OrderStatus, UserRole
from src.exceptions import (
    AuthorizationError,
    InvalidStatusTransitionError,
    NotFoundError,
    OrderNotModifiableError,
)
from src.factories import OrderFactory
from src.models import OrderDocument, UserDocument
from src.repositories import OrderRepository
from src.schemas import (
    OrderCreate,
    OrderFilter,
    OrderStatusUpdate,
    OrderUpdate,
    PaginatedResponse,
)

logger = logging.getLogger(__name__)

_TERMINAL_STATUSES = (
    OrderStatus.ORDER_COMPLETE,
    OrderStatus.ORDER_CANCELLED,
)


class OrderService:
    """Orchestrates order business logic.

    Attributes:
        _repository (OrderRepository): Order data access.
        _factory (OrderFactory): Document construction and price computation.
    """

    def __init__(
        self,
        repository: OrderRepository,
        factory: OrderFactory,
    ) -> None:
        """Initialize with repository and factory dependencies.

        Args:
            repository (OrderRepository): The order repository interface.
            factory (OrderFactory): The order document factory.
        """
        self._repository: OrderRepository = repository
        self._factory: OrderFactory = factory

    async def create_order(
        self, data: OrderCreate, current_user: UserDocument
    ) -> OrderDocument:
        """Create a new order for the authenticated user.

        Args:
            data (OrderCreate): The validated creation request.
            current_user (UserDocument): The authenticated user placing the order.

        Returns:
            OrderDocument: The persisted order document.

        Raises:
            MenuItemUnavailableError: If any requested item is unavailable.
        """
        logger.info(f"Creating order for user '{current_user.username}'")
        order_data = OrderCreate(
            orderer_name=current_user.username,
            items=data.items,
        )
        order = await self._factory.create(order_data)
        return await self._repository.create(order)

    async def get_order(
        self, order_number: int, current_user: UserDocument
    ) -> OrderDocument:
        """Retrieve a single order, enforcing guest ownership rules.

        Args:
            order_number (int): The order to retrieve.
            current_user (UserDocument): The authenticated requesting user.

        Returns:
            OrderDocument: The found order document.

        Raises:
            NotFoundError: If no order exists with this number.
            AuthorizationError: If a guest tries to access another's order.
        """
        logger.info(f"Fetching order {order_number}")
        order = await self._get_existing_order(order_number)
        self._check_ownership(order, current_user)
        return order

    async def get_all_orders(
        self,
        skip: int,
        limit: int,
        filters: OrderFilter,
        current_user: UserDocument,
    ) -> PaginatedResponse[OrderDocument]:
        """Retrieve a paginated, filtered list of orders.

        Args:
            skip (int): Number of documents to skip.
            limit (int): Maximum number of documents to return.
            filters (OrderFilter): Filter criteria from query parameters.
            current_user (UserDocument): The authenticated requesting user.

        Returns:
            PaginatedResponse[OrderDocument]: Paginated results with metadata.
        """
        logger.info(f"Listing orders skip={skip} limit={limit}")
        filter_dict = filters.model_dump(exclude_none=True)
        if current_user.role == UserRole.GUEST:
            filter_dict["orderer_name"] = current_user.username
        orders = await self._repository.get_all(skip, limit, filter_dict)
        total = await self._repository.count(filter_dict)
        return PaginatedResponse(
            items=orders,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total,
        )

    async def update_order(
        self,
        order_number: int,
        data: OrderUpdate,
        current_user: UserDocument,
    ) -> OrderDocument:
        """Update an existing order's details.

        Args:
            order_number (int): The order to update.
            data (OrderUpdate): The validated update request.
            current_user (UserDocument): The authenticated requesting user.

        Returns:
            OrderDocument: The updated order document.

        Raises:
            NotFoundError: If the order does not exist.
            AuthorizationError: If a guest accesses another user's order.
            OrderNotModifiableError: If the order is complete or cancelled.
        """
        logger.info(f"Updating order {order_number}")
        order = await self._get_existing_order(order_number)
        self._check_ownership(order, current_user)
        self._check_modifiable(order)
        update_data: Dict[str, Any] = {}
        if data.orderer_name is not None:
            update_data["orderer_name"] = data.orderer_name
        if data.items is not None:
            price_snapshot, total_price = await self._factory.compute_total(
                data.items
            )
            update_data["items"] = data.items
            update_data["item_price_snapshot"] = price_snapshot
            update_data["total_price"] = total_price
        update_data["updated_at"] = datetime.now(timezone.utc)
        return await self._apply_update(order.id, update_data)

    async def delete_order(
        self, order_number: int, current_user: UserDocument
    ) -> None:
        """Delete an existing order.

        Args:
            order_number (int): The order to delete.
            current_user (UserDocument): The authenticated requesting user.

        Raises:
            NotFoundError: If the order does not exist.
            AuthorizationError: If a guest accesses another user's order.
            OrderNotModifiableError: If the order is complete or cancelled.
        """
        logger.info(f"Deleting order {order_number}")
        order = await self._get_existing_order(order_number)
        self._check_ownership(order, current_user)
        self._check_modifiable(order)
        await self._repository.delete(order.id)

    async def update_order_status(
        self,
        order_number: int,
        data: OrderStatusUpdate,
        current_user: UserDocument,
    ) -> OrderDocument:
        """Update an order's lifecycle status.

        Args:
            order_number (int): The order to update.
            data (OrderStatusUpdate): The new status.
            current_user (UserDocument): The authenticated worker or admin.

        Returns:
            OrderDocument: The updated order document.

        Raises:
            NotFoundError: If the order does not exist.
            InvalidStatusTransitionError: If the transition is disallowed
                for the current role.
        """
        logger.info(
            f"Updating status of order {order_number} to {data.status}"
        )
        order = await self._get_existing_order(order_number)
        if current_user.role != UserRole.ADMINISTRATOR:
            self._validate_transition(order.status, data.status)
        update_data: Dict[str, Any] = {
            "status": data.status,
            "updated_at": datetime.now(timezone.utc),
        }
        return await self._apply_update(order.id, update_data)

    async def _get_existing_order(self, order_number: int) -> OrderDocument:
        """Fetch an order by business number or raise if not found.

        Args:
            order_number (int): The order business identifier.

        Returns:
            OrderDocument: The found order document.

        Raises:
            NotFoundError: If no order exists with the given number.
        """
        order = await self._repository.get_by_order_number(order_number)
        if order is None:
            raise NotFoundError(
                f"Order with number {order_number} not found"
            )
        return order

    def _check_ownership(
        self, order: OrderDocument, current_user: UserDocument
    ) -> None:
        """Enforce that guests can only access their own orders.

        Args:
            order (OrderDocument): The order being accessed.
            current_user (UserDocument): The authenticated user.

        Raises:
            AuthorizationError: If a guest accesses another user's order.
        """
        if (
            current_user.role == UserRole.GUEST
            and order.orderer_name != current_user.username
        ):
            raise AuthorizationError(
                "You are not authorized to access this order"
            )

    def _check_modifiable(self, order: OrderDocument) -> None:
        """Ensure the order is not in a terminal state.

        Args:
            order (OrderDocument): The order to check.

        Raises:
            OrderNotModifiableError: If the order is complete or cancelled.
        """
        if order.status in _TERMINAL_STATUSES:
            raise OrderNotModifiableError(
                f"Order {order.order_number} cannot be modified — "
                f"status is '{order.status.value}'"
            )

    async def _apply_update(
        self, internal_id: Any, update_data: Dict[str, Any]
    ) -> OrderDocument:
        """Commit the update to the repository.

        Args:
            internal_id (Any): The internal database ID.
            update_data (Dict[str, Any]): The fields and values to update.

        Returns:
            OrderDocument: The updated order document.

        Raises:
            NotFoundError: If the update fails because the record was
                not found.
        """
        updated = await self._repository.update(internal_id, update_data)
        if updated is None:
            raise NotFoundError("Order record missing during update")
        return updated

    @staticmethod
    def _validate_transition(
        current: OrderStatus, new: OrderStatus
    ) -> None:
        """Verify that the status transition is allowed for workers.

        Args:
            current (OrderStatus): The current order status.
            new (OrderStatus): The requested new status.

        Raises:
            InvalidStatusTransitionError: If the transition is not in
                the allowed transitions list.
        """
        if (current.value, new.value) not in WORKER_ALLOWED_TRANSITIONS:
            raise InvalidStatusTransitionError(
                f"Transition from '{current.value}' to '{new.value}' "
                f"is not allowed"
            )
