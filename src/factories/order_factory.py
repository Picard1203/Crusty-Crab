"""Factory for constructing OrderDocument instances."""

import logging
from datetime import datetime, timezone
from typing import Any, List, Tuple

from src.constants.sequence_constants import ORDER_NUMBER_SEQUENCE
from src.enums import OrderStatus
from src.exceptions import MenuItemUnavailableException
from src.factories.document_factory import DocumentFactory
from src.models import OrderDocument
from src.repositories import CounterRepository, MenuItemRepository
from src.schemas import OrderCreate

logger = logging.getLogger(__name__)


class OrderFactory(DocumentFactory):
    """Constructs OrderDocument instances with auto-increment IDs.

    Attributes:
        _counter_repo (CounterRepository): Repository for atomic ID generation.
        _menu_item_repo (MenuItemRepository): Repository for menu item lookups.
    """

    def __init__(
        self,
        counter_repo: CounterRepository,
        menu_item_repo: MenuItemRepository,
    ) -> None:
        """Initialize with counter and menu item repository dependencies.

        Args:
            counter_repo (CounterRepository): For generating auto-increment IDs.
            menu_item_repo (MenuItemRepository): For resolving item prices.
        """
        self._counter_repo: CounterRepository = counter_repo
        self._menu_item_repo: MenuItemRepository = menu_item_repo

    async def create(
        self,
        data: OrderCreate,
        **kwargs: Any,  # noqa: ARG002
    ) -> OrderDocument:
        """Construct a new OrderDocument from creation request data.

        Args:
            data (OrderCreate): The validated order creation schema.
            **kwargs (Any): Not used. Present for ABC compliance.

        Returns:
            OrderDocument: The constructed document, ready for persistence.

        Raises:
            MenuItemUnavailableException: If any item is not in the menu
                or is inactive.
        """
        order_number = await self._counter_repo.get_next_sequence(
            ORDER_NUMBER_SEQUENCE
        )
        price_snapshot, total_price = await self.compute_total(data.items)
        now = datetime.now(timezone.utc)
        logger.info(
            f"Constructing order document with order_number {order_number}"
        )
        return OrderDocument(
            order_number=order_number,
            orderer_name=data.orderer_name,
            items=data.items,
            item_price_snapshot=price_snapshot,
            total_price=total_price,
            status=OrderStatus.ORDER_RECEIVED,
            created_at=now,
            updated_at=now,
        )

    async def compute_total(
        self, items: List[str]
    ) -> Tuple[List[float], float]:
        """Resolve item prices and compute the total order cost.

        Args:
            items (List[str]): List of menu item names to price.

        Returns:
            Tuple[List[float], float]: (price_snapshot, total_price).

        Raises:
            MenuItemUnavailableException: If any item is not found
                in the menu or is marked inactive.
        """
        price_snapshot: List[float] = []
        for item_name in items:
            menu_item = await self._menu_item_repo.get_by_name(item_name)
            if menu_item is None or menu_item.is_active is False:
                raise MenuItemUnavailableException(
                    f"Menu item '{item_name}' is not available"
                )
            price_snapshot.append(menu_item.price)
        total_price = sum(price_snapshot)
        return price_snapshot, total_price
